#!/usr/bin/env python3
"""Import helper for the personality knowledge base.

The importer keeps a JSONDB queue of discovered sources and imports Wikipedia
article summaries as attributed Markdown cards. It intentionally avoids full
article dumps by default because this repository is public.
"""

from __future__ import annotations

import argparse
import email.utils
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(".")
JSONDB = ROOT / "jsondb"
IMPORT_QUEUE = JSONDB / "import_queue.json"
IMPORT_RUNS = JSONDB / "import_runs.json"
TERM_INVENTORY = JSONDB / "term_inventory.json"
WIKI_REVIEW = JSONDB / "wiki_import_review.json"
PAPER_REVIEW = JSONDB / "paper_import_review.json"
WIKI_IMPORTS = ROOT / "kb" / "wiki_imports"
PAPER_IMPORTS = ROOT / "kb" / "paper_imports"
SOURCES_DIR = ROOT / "sources"
USER_AGENT = "sol-personality-rag/0.1 (research import; contact: local)"
WIKIMEDIA_DEFAULT_SLEEP_SECONDS = 12.0
WIKIMEDIA_MIN_RETRY_SECONDS = 5.0


class RetryableHttpError(RuntimeError):
    """HTTP response that should pause or stop an import batch."""

    def __init__(self, status: int, url: str, retry_after_seconds: float | None = None) -> None:
        self.status = status
        self.url = url
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"HTTP {status} for {url}")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")[:120] or "item"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        retry_at = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())


def rate_limit_sleep_seconds(exc: RetryableHttpError, fallback: float) -> float:
    return max(exc.retry_after_seconds or WIKIMEDIA_MIN_RETRY_SECONDS, fallback)


def progress_log(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def clean_multiline_text(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.splitlines()).strip()


def request_json(url: str, timeout: float = 30) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in {429, 503}:
            raise RetryableHttpError(exc.code, url, parse_retry_after(exc.headers.get("Retry-After"))) from exc
        raise


def ensure_db() -> None:
    JSONDB.mkdir(parents=True, exist_ok=True)
    WIKI_IMPORTS.mkdir(parents=True, exist_ok=True)
    PAPER_IMPORTS.mkdir(parents=True, exist_ok=True)
    if not IMPORT_QUEUE.exists():
        save_json(IMPORT_QUEUE, {"version": 1, "items": []})
    if not IMPORT_RUNS.exists():
        save_json(IMPORT_RUNS, {"version": 1, "runs": []})
    if not PAPER_REVIEW.exists():
        save_json(PAPER_REVIEW, {"version": 1, "rejected_items": [], "deferred_items": [], "manual_matches": []})


def load_queue() -> dict[str, Any]:
    ensure_db()
    return load_json(IMPORT_QUEUE, {"version": 1, "items": []})


def save_queue(queue: dict[str, Any]) -> None:
    save_json(IMPORT_QUEUE, queue)


def load_paper_review() -> dict[str, Any]:
    ensure_db()
    return load_json(PAPER_REVIEW, {"version": 1, "rejected_items": [], "deferred_items": [], "manual_matches": []})


def add_queue_item(queue: dict[str, Any], item: dict[str, Any]) -> bool:
    existing = {entry["id"]: entry for entry in queue["items"]}
    if item["id"] in existing:
        target = existing[item["id"]]
        discovered_from = set(target.get("discovered_from", []))
        discovered_from.update(item.get("discovered_from", []))
        target["discovered_from"] = sorted(discovered_from)
        if item.get("imported"):
            target["imported"] = True
            target["imported_path"] = item.get("imported_path")
            target["imported_at"] = item.get("imported_at", utc_now())
            target["kind"] = item.get("kind", target.get("kind"))
        for key in ("title", "url", "domain", "term"):
            if item.get(key) and not target.get(key):
                target[key] = item[key]
        notes = set(target.get("notes", []))
        notes.update(item.get("notes", []))
        target["notes"] = sorted(notes)
        return False
    queue["items"].append(item)
    return True


def append_run_log(run: dict[str, Any]) -> None:
    data = load_json(IMPORT_RUNS, {"version": 1, "runs": []})
    data["runs"].append(run)
    save_json(IMPORT_RUNS, data)


def source_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(SOURCES_DIR.glob("*.json")):
        data = load_json(path, {})
        for source in data.get("sources", []):
            source = dict(source)
            source["_registry_path"] = path.as_posix()
            entries.append(source)
    return entries


def normalize_doi(doi: str) -> str:
    doi = doi.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = doi.rstrip(".,;:)]}")
    return doi


def doi_url(doi: str) -> str:
    return f"https://doi.org/{normalize_doi(doi)}"


def crossref_work(doi: str, timeout: float = 30) -> dict[str, Any]:
    encoded = urllib.parse.quote(normalize_doi(doi), safe="")
    return request_json(f"https://api.crossref.org/works/{encoded}", timeout=timeout)["message"]


def normalize_title_for_match(title: str) -> str:
    title = title.lower()
    title = (
        title.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )
    title = title.replace("&", "and")
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return " ".join(title.split())


def build_title_variants(title: str) -> list[str]:
    variants = [title.strip()]
    stripped = title.strip().rstrip(".")
    if stripped not in variants:
        variants.append(stripped)
    if ":" in stripped:
        variants.append(stripped.split(":", 1)[0].strip())
    if "?" in stripped:
        variants.append(stripped.split("?", 1)[0].strip())
    if "(" in stripped:
        variants.append(re.sub(r"\([^)]*\)", "", stripped).strip())

    normalized = []
    seen = set()
    for variant in variants:
        variant = re.sub(r"\s+", " ", variant).strip(" -:;,.")
        if variant and variant not in seen:
            seen.add(variant)
            normalized.append(variant)
    return normalized


def crossref_search_title(title: str, rows: int = 8, timeout: float = 5.0) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "query.title": title,
            "rows": rows,
        }
    )
    url = f"https://api.crossref.org/works?{params}"
    result = subprocess.run(
        [
            "curl",
            "--silent",
            "--show-error",
            "--location",
            "--max-time",
            str(timeout),
            "-A",
            USER_AGENT,
            url,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout + 1.0,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"curl failed with exit code {result.returncode}")
    return json.loads(result.stdout).get("message", {}).get("items", [])


def overlap_ratio(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / max(len(left), len(right))


def score_crossref_title_match(target_title: str, candidate_title: str, target_year: Any, candidate_year: int | None) -> int:
    normalized_target = normalize_title_for_match(target_title)
    normalized_candidate = normalize_title_for_match(candidate_title)
    if not normalized_target or not normalized_candidate:
        return -1

    target_tokens = set(normalized_target.split())
    candidate_tokens = set(normalized_candidate.split())
    token_overlap = len(target_tokens & candidate_tokens)
    ratio = overlap_ratio(target_tokens, candidate_tokens)
    score = 0

    if normalized_candidate == normalized_target:
        score += 120
    elif normalized_candidate.startswith(normalized_target) or normalized_target.startswith(normalized_candidate):
        score += 80
    elif normalized_target in normalized_candidate or normalized_candidate in normalized_target:
        score += 55

    score += token_overlap * 4
    score += int(ratio * 40)

    target_year_str = str(target_year) if target_year else None
    target_year_int = int(target_year_str) if target_year_str and target_year_str.isdigit() else None
    if target_year_str and candidate_year is not None:
        if str(candidate_year) == target_year_str:
            score += 20
        elif target_year_int is not None and abs(candidate_year - target_year_int) <= 1:
            score += 8
        elif target_year_int is not None and abs(candidate_year - target_year_int) >= 5:
            score -= 15

    short_target = len(target_tokens) <= 3
    if short_target and ratio < 1.0:
        score -= 40
    elif ratio < 0.6:
        score -= 20

    return score


def resolve_crossref_by_title(title: str, year: Any = None) -> dict[str, Any] | None:
    best_work: dict[str, Any] | None = None
    best_score = -1

    for variant in build_title_variants(title):
        try:
            results = crossref_search_title(variant)
        except Exception:
            if best_work is not None:
                continue
            raise
        for work in results:
            candidate_title = first_value(work.get("title"))
            if not candidate_title:
                continue
            candidate_year = published_year(work)
            score = score_crossref_title_match(title, candidate_title, year, candidate_year)
            if score > best_score:
                best_score = score
                best_work = work

    if best_score < 85:
        return None
    return best_work


def reviewed_paper_state(item: dict[str, Any], review: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    item_id = item.get("id")
    title = normalize_title_for_match(item.get("title") or "")
    for entry in review.get("rejected_items", []):
        if entry.get("id") == item_id or (title and normalize_title_for_match(entry.get("title") or "") == title):
            return "rejected", entry
    for entry in review.get("deferred_items", []):
        if entry.get("id") == item_id or (title and normalize_title_for_match(entry.get("title") or "") == title):
            return "deferred", entry
    for entry in review.get("manual_matches", []):
        if entry.get("id") == item_id or (title and normalize_title_for_match(entry.get("title") or "") == title):
            return "manual", entry
    return None, None


def queue_crossref_references(limit: int | None = None, sleep_seconds: float = 0.2) -> dict[str, int]:
    queue = load_queue()
    added = 0
    checked = 0
    skipped = 0

    for source in source_entries():
        doi = source.get("doi")
        if not doi:
            skipped += 1
            continue
        if limit is not None and checked >= limit:
            break
        checked += 1
        try:
            work = crossref_work(doi)
        except Exception as exc:  # noqa: BLE001 - import queue should log and continue.
            add_queue_item(
                queue,
                {
                    "id": f"error:crossref:{normalize_doi(doi)}",
                    "kind": "import_error",
                    "title": f"Crossref import failed for {source.get('id', doi)}",
                    "url": doi_url(doi),
                    "discovered_from": [source.get("id", normalize_doi(doi))],
                    "imported": False,
                    "imported_path": None,
                    "priority": "review",
                    "notes": [str(exc)],
                    "created_at": utc_now(),
                },
            )
            continue

        for ref in work.get("reference", []):
            ref_doi = ref.get("DOI") or ref.get("doi")
            title = ref.get("article-title") or ref.get("series-title") or ref.get("journal-title")
            if not ref_doi and not title:
                continue
            if ref_doi:
                item_id = f"paper:{normalize_doi(ref_doi).lower()}"
                url = doi_url(ref_doi)
            else:
                item_id = f"paper-title:{slugify(title)}"
                url = None
            item = {
                "id": item_id,
                "kind": "paper_reference",
                "title": title or normalize_doi(ref_doi),
                "doi": normalize_doi(ref_doi) if ref_doi else None,
                "url": url,
                "year": ref.get("year"),
                "container_title": ref.get("journal-title"),
                "first_page": ref.get("first-page"),
                "discovered_from": [source.get("id", normalize_doi(doi))],
                "imported": False,
                "imported_path": None,
                "priority": "normal",
                "notes": [],
                "created_at": utc_now(),
            }
            if add_queue_item(queue, item):
                added += 1
        time.sleep(sleep_seconds)

    save_queue(queue)
    result = {"sources_checked": checked, "sources_skipped": skipped, "queue_items_added": added}
    append_run_log({"type": "queue_crossref_references", "timestamp": utc_now(), "result": result})
    return result


def load_terms() -> list[dict[str, str]]:
    data = load_json(TERM_INVENTORY, {"terms": []})
    return data.get("terms", [])


def queue_wikipedia_terms() -> dict[str, int]:
    queue = load_queue()
    added = 0
    for entry in load_terms():
        term = entry["term"]
        domain = entry.get("domain", "unknown")
        if add_queue_item(
            queue,
            {
                "id": f"wikipedia-term:{slugify(term)}",
                "kind": "wikipedia_term",
                "title": term,
                "term": term,
                "url": f"https://en.wikipedia.org/w/index.php?search={urllib.parse.quote(term)}",
                "domain": domain,
                "discovered_from": ["term_inventory"],
                "imported": False,
                "imported_path": None,
                "priority": "background",
                "notes": ["Queued from curated term inventory."],
                "created_at": utc_now(),
            },
        ):
            added += 1
    save_queue(queue)
    result = {"terms_queued": added, "terms_total": len(load_terms())}
    append_run_log({"type": "queue_wikipedia_terms", "timestamp": utc_now(), "result": result})
    return result


def wikipedia_page(term: str, link_limit: int = 25) -> dict[str, Any] | None:
    query = {
        "action": "query",
        "generator": "search",
        "gsrsearch": term,
        "gsrlimit": 1,
        "prop": "extracts|info",
        "exintro": 1,
        "explaintext": 1,
        "inprop": "url",
        "format": "json",
        "utf8": 1,
    }
    if link_limit > 0:
        query["prop"] = "extracts|links|info"
        query["pllimit"] = min(link_limit, 50)
    params = urllib.parse.urlencode(query)
    data = request_json(f"https://en.wikipedia.org/w/api.php?{params}")
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None
    page = next(iter(pages.values()))
    links = [
        link["title"]
        for link in page.get("links", [])
        if link.get("title") and not link["title"].startswith(("Help:", "File:", "Template:", "Wikipedia:"))
    ]
    return {
        "title": page.get("title") or term,
        "extract": page.get("extract") or "",
        "content_urls": {"desktop": {"page": page.get("fullurl")}},
        "description": "",
        "links": links,
    }


def wikipedia_page_by_title(title: str, link_limit: int = 25) -> dict[str, Any] | None:
    query = {
        "action": "query",
        "titles": title,
        "redirects": 1,
        "prop": "extracts|info",
        "exintro": 1,
        "explaintext": 1,
        "inprop": "url",
        "format": "json",
        "utf8": 1,
    }
    if link_limit > 0:
        query["prop"] = "extracts|links|info"
        query["pllimit"] = min(link_limit, 50)
    params = urllib.parse.urlencode(query)
    data = request_json(f"https://en.wikipedia.org/w/api.php?{params}")
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None
    page = next(iter(pages.values()))
    if page.get("missing") is not None:
        return None
    links = [
        link["title"]
        for link in page.get("links", [])
        if link.get("title") and not link["title"].startswith(("Help:", "File:", "Template:", "Wikipedia:"))
    ]
    return {
        "title": page.get("title") or title,
        "extract": page.get("extract") or "",
        "content_urls": {"desktop": {"page": page.get("fullurl")}},
        "description": "",
        "links": links,
    }


def write_wiki_card(term: str, domain: str, summary: dict[str, Any]) -> Path:
    title = summary.get("title") or term
    page_url = summary.get("content_urls", {}).get("desktop", {}).get("page") or summary.get("canonicalurl")
    extract = clean_multiline_text(summary.get("extract") or "")
    description = clean_multiline_text(summary.get("description") or "")
    path = WIKI_IMPORTS / f"{slugify(title)}.md"
    text = f"""# Wikipedia Import: {title}

## Matched Term

{term}

## Domain

{domain}

## Source

{page_url}

## Description

{description}

## Summary

{extract}

## Import Policy

This card imports the Wikipedia article summary, not the full article text.
Wikipedia content is licensed under CC BY-SA; use the source URL for full
attribution and further review before promoting article content into reviewed
project knowledge.

## Import Status

Imported as background reference. Not a peer-reviewed source.
"""
    path.write_text(text, encoding="utf-8")
    return path


def import_queued_wikipedia(
    limit: int | None = None,
    link_limit: int = 0,
    sleep_seconds: float = WIKIMEDIA_DEFAULT_SLEEP_SECONDS,
    progress: bool = False,
) -> dict[str, Any]:
    queue = load_queue()
    candidates = [
        item
        for item in queue["items"]
        if item.get("kind") == "wikipedia_linked_article" and not item.get("imported")
    ]
    if limit is not None:
        candidates = candidates[:limit]

    imported = 0
    linked_added = 0
    errors = 0
    checked = 0
    stopped_after_rate_limit = False
    rate_limit_retry_after_seconds: float | None = None

    for item in candidates:
        title = item.get("title") or item.get("term")
        if not title:
            continue
        checked += 1
        domain = item.get("domain", "unknown")
        progress_log(progress, f"[wiki-queue {checked}/{len(candidates)}] title={title!r} domain={domain!r}")
        try:
            summary = wikipedia_page_by_title(title, link_limit=link_limit)
            if not summary:
                progress_log(progress, f"[wiki-queue {checked}/{len(candidates)}] no exact title match; sleeping {sleep_seconds}s before search")
                time.sleep(sleep_seconds)
                summary = wikipedia_page(title, link_limit=link_limit)
            if not summary:
                errors += 1
                notes = set(item.get("notes", []))
                notes.add("Queued Wikipedia import found no matching page.")
                item["notes"] = sorted(notes)
                save_queue(queue)
                progress_log(progress, f"[wiki-queue {checked}/{len(candidates)}] no matching page; sleeping {sleep_seconds}s")
                time.sleep(sleep_seconds)
                continue

            resolved_title = summary.get("title") or title
            path = write_wiki_card(title, domain, summary)
            page_url = summary.get("content_urls", {}).get("desktop", {}).get("page")
            item["kind"] = "wikipedia_article"
            item["title"] = resolved_title
            item["term"] = title
            item["url"] = page_url
            item["imported"] = True
            item["imported_path"] = path.as_posix()
            item["imported_at"] = utc_now()
            notes = set(item.get("notes", []))
            notes.add("Imported queued linked Wikipedia summary; full article not imported by default.")
            item["notes"] = sorted(notes)
            imported += 1
            progress_log(
                progress,
                f"[wiki-queue {checked}/{len(candidates)}] imported title={resolved_title!r} path={path.as_posix()}",
            )

            for linked_title in summary.get("links", []):
                linked_item = {
                    "id": f"wikipedia:{slugify(linked_title)}",
                    "kind": "wikipedia_linked_article",
                    "title": linked_title,
                    "term": linked_title,
                    "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(linked_title.replace(' ', '_'))}",
                    "domain": domain,
                    "discovered_from": [f"wikipedia:{slugify(resolved_title)}"],
                    "imported": False,
                    "imported_path": None,
                    "priority": "background",
                    "notes": ["Discovered from imported queued Wikipedia article links."],
                    "created_at": utc_now(),
                }
                if add_queue_item(queue, linked_item):
                    linked_added += 1
            save_queue(queue)
            progress_log(progress, f"[wiki-queue {checked}/{len(candidates)}] sleeping {sleep_seconds}s")
            time.sleep(sleep_seconds)
        except RetryableHttpError as exc:
            errors += 1
            stopped_after_rate_limit = True
            rate_limit_retry_after_seconds = exc.retry_after_seconds
            notes = set(item.get("notes", []))
            notes.add(
                f"Pending retry after Wikimedia HTTP {exc.status}; "
                f"retry_after_seconds={exc.retry_after_seconds or 'unknown'}."
            )
            item["notes"] = sorted(notes)
            save_queue(queue)
            pause = rate_limit_sleep_seconds(exc, sleep_seconds)
            progress_log(
                progress,
                f"[wiki-queue {checked}/{len(candidates)}] rate limited HTTP {exc.status}; "
                f"retry_after={exc.retry_after_seconds}; sleeping {pause}s and stopping",
            )
            time.sleep(pause)
            break
        except Exception as exc:  # noqa: BLE001 - queue import should log and continue.
            errors += 1
            notes = set(item.get("notes", []))
            notes.add(f"Pending retry after queued Wikipedia import error: {exc}")
            item["notes"] = sorted(notes)
            save_queue(queue)
            progress_log(progress, f"[wiki-queue {checked}/{len(candidates)}] error={exc}; sleeping {sleep_seconds}s")
            time.sleep(sleep_seconds)

    save_queue(queue)
    result = {
        "candidates_checked": checked,
        "candidates_planned": len(candidates),
        "summaries_imported": imported,
        "linked_articles_added": linked_added,
        "errors": errors,
        "stopped_after_rate_limit": stopped_after_rate_limit,
        "rate_limit_retry_after_seconds": rate_limit_retry_after_seconds,
    }
    append_run_log({"type": "import_queued_wikipedia", "timestamp": utc_now(), "result": result})
    return result


def import_wikipedia(
    limit: int | None = None,
    link_limit: int = 25,
    sleep_seconds: float = WIKIMEDIA_DEFAULT_SLEEP_SECONDS,
    progress: bool = False,
) -> dict[str, Any]:
    queue = load_queue()
    imported = 0
    skipped_existing = 0
    linked_added = 0
    errors = 0
    checked = 0
    stopped_after_rate_limit = False
    rate_limit_retry_after_seconds: float | None = None
    terms = load_terms()
    if limit is not None:
        terms = terms[:limit]

    for entry in terms:
        term = entry["term"]
        domain = entry.get("domain", "unknown")
        already_imported_terms = {
            item.get("term", "").lower()
            for item in queue["items"]
            if item.get("kind") == "wikipedia_article" and item.get("imported")
        }
        if term.lower() in already_imported_terms:
            skipped_existing += 1
            continue
        checked += 1
        progress_log(progress, f"[wiki-term {checked}/{len(terms)}] term={term!r} domain={domain!r}")
        try:
            summary = wikipedia_page(term, link_limit=link_limit)
            if not summary:
                errors += 1
                save_queue(queue)
                progress_log(progress, f"[wiki-term {checked}/{len(terms)}] no matching page; sleeping {sleep_seconds}s")
                time.sleep(sleep_seconds)
                continue
            title = summary.get("title") or term
            path = write_wiki_card(term, domain, summary)
            page_url = summary.get("content_urls", {}).get("desktop", {}).get("page")
            term_queue_id = f"wikipedia-term:{slugify(term)}"
            add_queue_item(
                queue,
                {
                    "id": term_queue_id,
                    "kind": "wikipedia_term",
                    "title": term,
                    "term": term,
                    "url": page_url,
                    "domain": domain,
                    "discovered_from": ["term_inventory"],
                    "imported": True,
                    "imported_path": path.as_posix(),
                    "priority": "background",
                    "notes": ["Resolved to imported Wikipedia article summary."],
                    "created_at": utc_now(),
                    "imported_at": utc_now(),
                },
            )
            add_queue_item(
                queue,
                {
                    "id": f"wikipedia:{slugify(title)}",
                    "kind": "wikipedia_article",
                    "title": title,
                    "term": term,
                    "url": page_url,
                    "domain": domain,
                    "discovered_from": ["term_inventory"],
                    "imported": True,
                    "imported_path": path.as_posix(),
                    "priority": "background",
                    "notes": ["Imported summary only; full article not imported by default."],
                    "created_at": utc_now(),
                    "imported_at": utc_now(),
                },
            )
            imported += 1
            progress_log(progress, f"[wiki-term {checked}/{len(terms)}] imported title={title!r} path={path.as_posix()}")

            for linked_title in summary.get("links", []):
                linked_item = {
                    "id": f"wikipedia:{slugify(linked_title)}",
                    "kind": "wikipedia_linked_article",
                    "title": linked_title,
                    "term": linked_title,
                    "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(linked_title.replace(' ', '_'))}",
                    "domain": domain,
                    "discovered_from": [f"wikipedia:{slugify(title)}"],
                    "imported": False,
                    "imported_path": None,
                    "priority": "background",
                    "notes": ["Discovered from imported Wikipedia article links."],
                    "created_at": utc_now(),
                }
                if add_queue_item(queue, linked_item):
                    linked_added += 1
            save_queue(queue)
            progress_log(progress, f"[wiki-term {checked}/{len(terms)}] sleeping {sleep_seconds}s")
            time.sleep(sleep_seconds)
        except RetryableHttpError as exc:
            errors += 1
            stopped_after_rate_limit = True
            rate_limit_retry_after_seconds = exc.retry_after_seconds
            add_queue_item(
                queue,
                {
                    "id": f"wikipedia-term:{slugify(term)}",
                    "kind": "wikipedia_term",
                    "title": term,
                    "term": term,
                    "url": f"https://en.wikipedia.org/w/index.php?search={urllib.parse.quote(term)}",
                    "domain": domain,
                    "discovered_from": ["term_inventory"],
                    "imported": False,
                    "imported_path": None,
                    "priority": "background",
                    "notes": [
                        f"Pending retry after Wikimedia HTTP {exc.status}; "
                        f"retry_after_seconds={exc.retry_after_seconds or 'unknown'}."
                    ],
                    "created_at": utc_now(),
                },
            )
            save_queue(queue)
            pause = rate_limit_sleep_seconds(exc, sleep_seconds)
            progress_log(
                progress,
                f"[wiki-term {checked}/{len(terms)}] rate limited HTTP {exc.status}; "
                f"retry_after={exc.retry_after_seconds}; sleeping {pause}s and stopping",
            )
            time.sleep(pause)
            break
        except Exception as exc:  # noqa: BLE001 - import queue should log and continue.
            errors += 1
            add_queue_item(
                queue,
                {
                    "id": f"wikipedia-term:{slugify(term)}",
                    "kind": "wikipedia_term",
                    "title": term,
                    "term": term,
                    "url": f"https://en.wikipedia.org/w/index.php?search={urllib.parse.quote(term)}",
                    "domain": domain,
                    "discovered_from": ["term_inventory"],
                    "imported": False,
                    "imported_path": None,
                    "priority": "background",
                    "notes": [f"Pending retry after import error: {exc}"],
                    "created_at": utc_now(),
                },
            )
            add_queue_item(
                queue,
                {
                    "id": f"error:wikipedia:{slugify(term)}",
                    "kind": "import_error",
                    "title": f"Wikipedia import failed for {term}",
                    "term": term,
                    "domain": domain,
                    "discovered_from": ["term_inventory"],
                    "imported": False,
                    "imported_path": None,
                    "priority": "review",
                    "notes": [str(exc)],
                    "created_at": utc_now(),
                },
            )
            save_queue(queue)
            progress_log(progress, f"[wiki-term {checked}/{len(terms)}] error={exc}; sleeping {sleep_seconds}s")
            time.sleep(sleep_seconds)

    save_queue(queue)
    result = {
        "terms_checked": checked,
        "terms_planned": len(terms),
        "summaries_imported": imported,
        "skipped_existing": skipped_existing,
        "linked_articles_added": linked_added,
        "errors": errors,
        "stopped_after_rate_limit": stopped_after_rate_limit,
        "rate_limit_retry_after_seconds": rate_limit_retry_after_seconds,
    }
    append_run_log({"type": "import_wikipedia", "timestamp": utc_now(), "result": result})
    return result


def format_authors(work: dict[str, Any], limit: int = 12) -> str:
    authors = []
    for author in work.get("author", [])[:limit]:
        parts = [author.get("given"), author.get("family")]
        name = " ".join(part for part in parts if part)
        if name:
            authors.append(name)
    if len(work.get("author", [])) > limit:
        authors.append("et al.")
    return ", ".join(authors) if authors else "Unknown"


def first_value(values: Any) -> str | None:
    if isinstance(values, list) and values:
        return str(values[0])
    if values:
        return str(values)
    return None


def published_year(work: dict[str, Any]) -> int | None:
    for key in ("published-print", "published-online", "published", "issued"):
        parts = work.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            return parts[0][0]
    return None


def write_paper_metadata_card(item: dict[str, Any], work: dict[str, Any]) -> Path:
    title = first_value(work.get("title")) or item.get("title") or item.get("doi") or "Untitled paper"
    doi = normalize_doi(work.get("DOI") or item.get("doi") or "")
    url = work.get("URL") or doi_url(doi)
    container = first_value(work.get("container-title")) or item.get("container_title") or ""
    year = published_year(work) or item.get("year") or ""
    authors = format_authors(work)
    reference_count = work.get("reference-count", "")
    cited_by_count = work.get("is-referenced-by-count", "")
    source_ids = ", ".join(item.get("discovered_from", [])) or "unknown"
    path = PAPER_IMPORTS / f"{slugify(title)}.md"
    text = f"""# Paper Metadata Import: {title}

## Citation Metadata

- Authors: {authors}
- Year: {year}
- Venue: {container}
- DOI: {doi}
- URL: {url}

## Queue Metadata

- Queue id: `{item.get("id")}`
- Discovered from: {source_ids}
- Reference count: {reference_count}
- Crossref cited-by count: {cited_by_count}

## Import Policy

This card imports bibliographic metadata only. It does not import full paper
text or abstracts by default. Promote this paper into a reviewed source card
only after reading the source and recording project-specific implications,
limits, and evidence grade.

## Import Status

Imported as background paper metadata. Not yet reviewed into the knowledge
model.
"""
    path.write_text(text, encoding="utf-8")
    return path


def write_manual_paper_metadata_card(item: dict[str, Any], manual: dict[str, Any]) -> Path:
    title = manual.get("title") or item.get("title") or item.get("doi") or "Untitled source"
    doi = normalize_doi(manual.get("doi") or item.get("doi") or "")
    url = manual.get("url") or item.get("url") or (doi_url(doi) if doi else "")
    container = manual.get("container_title") or item.get("container_title") or ""
    year = manual.get("year") or item.get("year") or ""
    authors = manual.get("authors") or "Unknown"
    source_ids = ", ".join(item.get("discovered_from", [])) or "unknown"
    path = PAPER_IMPORTS / f"{slugify(title)}.md"
    text = f"""# Paper Metadata Import: {title}

## Citation Metadata

- Authors: {authors}
- Year: {year}
- Venue: {container}
- DOI: {doi}
- URL: {url}

## Queue Metadata

- Queue id: `{item.get("id")}`
- Discovered from: {source_ids}

## Import Policy

This card was imported from a manual metadata mapping because Crossref metadata
was unavailable or unsuitable for this source. It does not import full source
text or abstracts by default. Promote this source into a reviewed source card
only after reading the source and recording project-specific implications,
limits, and evidence grade.

## Import Status

Imported as background source metadata via manual review. Not yet reviewed into
the knowledge model.
"""
    path.write_text(text, encoding="utf-8")
    return path


def apply_paper_work_to_item(item: dict[str, Any], work: dict[str, Any], note: str) -> Path:
    doi = normalize_doi(work.get("DOI") or item.get("doi") or "")
    path = write_paper_metadata_card(item, work)
    item["title"] = first_value(work.get("title")) or item.get("title")
    item["doi"] = doi or item.get("doi")
    item["url"] = work.get("URL") or (doi_url(doi) if doi else item.get("url"))
    item["year"] = published_year(work) or item.get("year")
    item["container_title"] = first_value(work.get("container-title")) or item.get("container_title")
    item["imported"] = True
    item["imported_path"] = path.as_posix()
    item["imported_at"] = utc_now()
    notes = set(item.get("notes", []))
    notes = {entry for entry in notes if not entry.startswith("Pending retry after paper metadata import error:")}
    notes.add(note)
    item["notes"] = sorted(notes)
    return path


def apply_manual_paper_metadata_to_item(item: dict[str, Any], manual: dict[str, Any], note: str) -> Path:
    doi = normalize_doi(manual.get("doi") or item.get("doi") or "")
    path = write_manual_paper_metadata_card(item, manual)
    item["title"] = manual.get("title") or item.get("title")
    item["doi"] = doi or item.get("doi")
    item["url"] = manual.get("url") or item.get("url") or (doi_url(doi) if doi else None)
    item["year"] = manual.get("year") or item.get("year")
    item["container_title"] = manual.get("container_title") or item.get("container_title")
    item["imported"] = True
    item["imported_path"] = path.as_posix()
    item["imported_at"] = utc_now()
    notes = set(item.get("notes", []))
    notes = {entry for entry in notes if not entry.startswith("Pending retry after paper metadata import error:")}
    notes.add(note)
    item["notes"] = sorted(notes)
    return path


def apply_paper_review_state(item: dict[str, Any], status: str, review_entry: dict[str, Any]) -> None:
    item["review_status"] = status
    notes = set(item.get("notes", []))
    notes = {entry for entry in notes if not entry.startswith("Pending retry after paper metadata import error:")}
    reason = review_entry.get("reason") or "No reason recorded."
    notes.add(f"Paper review status: {status}. {reason}")
    item["notes"] = sorted(notes)


def import_paper_metadata(limit: int | None = None, sleep_seconds: float = 0.2) -> dict[str, int]:
    queue = load_queue()
    review = load_paper_review()
    candidates = [
        item
        for item in queue["items"]
        if item.get("kind") == "paper_reference"
        and not item.get("imported")
        and (item.get("doi") or item.get("title"))
    ]
    if limit is not None:
        candidates = candidates[:limit]

    imported = 0
    errors = 0
    skipped = 0
    rejected = 0
    deferred = 0
    for item in candidates:
        doi = item.get("doi")
        title = item.get("title")
        if not doi and not title:
            skipped += 1
            continue
        review_state, review_entry = reviewed_paper_state(item, review)
        if review_state == "rejected":
            apply_paper_review_state(item, "rejected", review_entry or {})
            rejected += 1
            save_queue(queue)
            continue
        if review_state == "deferred":
            apply_paper_review_state(item, "deferred", review_entry or {})
            deferred += 1
            save_queue(queue)
            continue
        try:
            work: dict[str, Any] | None = None
            note = "Imported Crossref bibliographic metadata only; source not reviewed."
            if review_state == "manual" and review_entry:
                manual_url = review_entry.get("url")
                manual_title = review_entry.get("title")
                manual_doi = review_entry.get("doi")
                if manual_doi and (manual_url or manual_title) and review_entry.get("source") != "crossref":
                    apply_manual_paper_metadata_to_item(
                        item,
                        review_entry,
                        "Imported manual bibliographic metadata only; source not reviewed. Resolved via manual source mapping.",
                    )
                    imported += 1
                    save_queue(queue)
                    time.sleep(sleep_seconds)
                    continue
                if manual_doi:
                    work = crossref_work(manual_doi)
                    note = (
                        "Imported Crossref bibliographic metadata only; source not reviewed. "
                        "Resolved via manual review DOI mapping."
                    )
                else:
                    raise RuntimeError("Manual paper match is missing a DOI.")
            elif doi:
                try:
                    work = crossref_work(doi)
                except Exception:
                    if title:
                        work = resolve_crossref_by_title(title, item.get("year"))
                        if work:
                            note = (
                                "Imported Crossref bibliographic metadata only; source not reviewed. "
                                "Resolved via Crossref title search fallback."
                            )
                    if not work:
                        raise
            elif title:
                work = resolve_crossref_by_title(title, item.get("year"))
                note = (
                    "Imported Crossref bibliographic metadata only; source not reviewed. "
                    "Resolved via Crossref title search."
                )
            if not work:
                raise RuntimeError("No Crossref title match found.")

            apply_paper_work_to_item(item, work, note)
            imported += 1
            save_queue(queue)
            time.sleep(sleep_seconds)
        except Exception as exc:  # noqa: BLE001 - queue import should log and continue.
            errors += 1
            notes = set(item.get("notes", []))
            notes.add(f"Pending retry after paper metadata import error: {exc}")
            item["notes"] = sorted(notes)
            save_queue(queue)

    save_queue(queue)
    result = {
        "candidates_checked": len(candidates),
        "metadata_cards_imported": imported,
        "skipped": skipped,
        "rejected": rejected,
        "deferred": deferred,
        "errors": errors,
    }
    append_run_log({"type": "import_paper_metadata", "timestamp": utc_now(), "result": result})
    return result


def import_paper_manual_matches(sleep_seconds: float = 0.0) -> dict[str, int]:
    queue = load_queue()
    review = load_paper_review()
    candidates = [
        item
        for item in queue["items"]
        if item.get("kind") == "paper_reference"
        and not item.get("imported")
        and reviewed_paper_state(item, review)[0] == "manual"
    ]

    imported = 0
    errors = 0
    for item in candidates:
        _state, review_entry = reviewed_paper_state(item, review)
        try:
            if not review_entry:
                raise RuntimeError("Missing manual review entry.")
            manual_url = review_entry.get("url")
            manual_title = review_entry.get("title")
            manual_doi = review_entry.get("doi")
            if manual_doi and (manual_url or manual_title) and review_entry.get("source") != "crossref":
                apply_manual_paper_metadata_to_item(
                    item,
                    review_entry,
                    "Imported manual bibliographic metadata only; source not reviewed. Resolved via manual source mapping.",
                )
            elif manual_doi:
                work = crossref_work(manual_doi)
                apply_paper_work_to_item(
                    item,
                    work,
                    "Imported Crossref bibliographic metadata only; source not reviewed. Resolved via manual review DOI mapping.",
                )
            else:
                raise RuntimeError("Manual review entry is missing a DOI.")
            imported += 1
            save_queue(queue)
            time.sleep(sleep_seconds)
        except Exception as exc:  # noqa: BLE001
            errors += 1
            notes = set(item.get("notes", []))
            notes.add(f"Pending retry after paper metadata import error: {exc}")
            item["notes"] = sorted(notes)
            save_queue(queue)

    save_queue(queue)
    result = {
        "candidates_checked": len(candidates),
        "metadata_cards_imported": imported,
        "errors": errors,
    }
    append_run_log({"type": "import_paper_manual_matches", "timestamp": utc_now(), "result": result})
    return result


def command_init_db(_: argparse.Namespace) -> None:
    ensure_db()
    print(f"Initialized JSONDB in {JSONDB}")


def command_queue_crossref(args: argparse.Namespace) -> None:
    result = queue_crossref_references(limit=args.limit, sleep_seconds=args.sleep)
    print(json.dumps(result, indent=2, sort_keys=True))


def command_queue_wikipedia_terms(_: argparse.Namespace) -> None:
    result = queue_wikipedia_terms()
    print(json.dumps(result, indent=2, sort_keys=True))


def command_import_wikipedia(args: argparse.Namespace) -> None:
    result = import_wikipedia(
        limit=args.limit,
        link_limit=args.link_limit,
        sleep_seconds=args.sleep,
        progress=not args.no_progress,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def command_import_queued_wikipedia(args: argparse.Namespace) -> None:
    result = import_queued_wikipedia(
        limit=args.limit,
        link_limit=args.link_limit,
        sleep_seconds=args.sleep,
        progress=not args.no_progress,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def command_import_paper_metadata(args: argparse.Namespace) -> None:
    result = import_paper_metadata(limit=args.limit, sleep_seconds=args.sleep)
    print(json.dumps(result, indent=2, sort_keys=True))


def command_import_paper_manual_matches(args: argparse.Namespace) -> None:
    result = import_paper_manual_matches(sleep_seconds=args.sleep)
    print(json.dumps(result, indent=2, sort_keys=True))


def command_run_initial(args: argparse.Namespace) -> None:
    ensure_db()
    wiki_result = import_wikipedia(
        limit=args.wiki_limit,
        link_limit=args.link_limit,
        sleep_seconds=args.sleep,
        progress=not args.no_progress,
    )
    reference_result = queue_crossref_references(limit=args.reference_limit, sleep_seconds=args.sleep)
    print(json.dumps({"wikipedia": wiki_result, "crossref": reference_result}, indent=2, sort_keys=True))


def command_clear_errors(_: argparse.Namespace) -> None:
    queue = load_queue()
    before = len(queue["items"])
    queue["items"] = [item for item in queue["items"] if item.get("kind") != "import_error"]
    save_queue(queue)
    result = {"removed": before - len(queue["items"]), "remaining": len(queue["items"])}
    append_run_log({"type": "clear_errors", "timestamp": utc_now(), "result": result})
    print(json.dumps(result, indent=2, sort_keys=True))


def command_sync_wikipedia_terms(_: argparse.Namespace) -> None:
    queue = load_queue()
    imported_articles = {
        item.get("term", "").lower(): item
        for item in queue["items"]
        if item.get("kind") == "wikipedia_article" and item.get("imported")
    }
    updated = 0
    for item in queue["items"]:
        if item.get("kind") != "wikipedia_term":
            continue
        article = imported_articles.get(item.get("term", "").lower())
        if not article:
            continue
        if not item.get("imported"):
            updated += 1
        item["imported"] = True
        item["imported_path"] = article.get("imported_path")
        item["imported_at"] = article.get("imported_at", utc_now())
        item["url"] = article.get("url", item.get("url"))
        notes = set(item.get("notes", []))
        notes.add("Synced with imported Wikipedia article summary.")
        item["notes"] = sorted(notes)
    save_queue(queue)
    result = {"wikipedia_terms_synced": updated}
    append_run_log({"type": "sync_wikipedia_terms", "timestamp": utc_now(), "result": result})
    print(json.dumps(result, indent=2, sort_keys=True))


def command_apply_wiki_review(_: argparse.Namespace) -> None:
    review = load_json(WIKI_REVIEW, {"rejected_mappings": []})
    rejected = {item["article_id"]: item for item in review.get("rejected_mappings", [])}
    rejected_terms = {item["term"].lower(): item for item in review.get("rejected_mappings", [])}
    queue = load_queue()
    updated = 0
    deleted_files = 0

    for item in queue["items"]:
        rejection = rejected.get(item.get("id"))
        if not rejection:
            rejection = rejected_terms.get(item.get("term", "").lower()) if item.get("kind") == "wikipedia_term" else None
        if not rejection:
            continue

        imported_path = item.get("imported_path")
        if imported_path:
            path = Path(imported_path)
            if path.exists():
                path.unlink()
                deleted_files += 1

        item["imported"] = False
        item["imported_path"] = None
        item["kind"] = "wikipedia_rejected_article" if item.get("id") in rejected else item.get("kind")
        notes = set(item.get("notes", []))
        notes.add(f"Rejected Wikipedia mapping: {rejection['reason']}")
        item["notes"] = sorted(notes)
        updated += 1

    save_queue(queue)
    result = {"queue_items_updated": updated, "files_deleted": deleted_files}
    append_run_log({"type": "apply_wiki_review", "timestamp": utc_now(), "result": result})
    print(json.dumps(result, indent=2, sort_keys=True))


def command_apply_paper_review(_: argparse.Namespace) -> None:
    review = load_paper_review()
    queue = load_queue()
    updated = 0
    for item in queue["items"]:
        if item.get("kind") != "paper_reference" or item.get("imported"):
            continue
        review_state, review_entry = reviewed_paper_state(item, review)
        if review_state not in {"rejected", "deferred"}:
            continue
        apply_paper_review_state(item, review_state, review_entry or {})
        updated += 1

    save_queue(queue)
    result = {"queue_items_updated": updated}
    append_run_log({"type": "apply_paper_review", "timestamp": utc_now(), "result": result})
    print(json.dumps(result, indent=2, sort_keys=True))


def command_paper_review_report(args: argparse.Namespace) -> None:
    queue = load_queue()
    review = load_paper_review()
    pending = [item for item in queue["items"] if item.get("kind") == "paper_reference" and not item.get("imported")]
    pending.sort(key=lambda item: ((item.get("year") or ""), item.get("title") or ""))

    lines = [
        "# Paper Import Review Queue",
        "",
        f"Generated: {utc_now()}",
        "",
        f"- pending paper references: {len(pending)}",
        f"- rejected review entries: {len(review.get('rejected_items', []))}",
        f"- deferred review entries: {len(review.get('deferred_items', []))}",
        f"- manual DOI mappings: {len(review.get('manual_matches', []))}",
        "",
        "## Pending Items",
        "",
    ]

    for item in pending[: args.limit]:
        state, _entry = reviewed_paper_state(item, review)
        state_label = state or "unreviewed"
        title = item.get("title") or item.get("id")
        year = item.get("year") or "unknown"
        doi = item.get("doi") or "none"
        lines.append(f"- [{state_label}] {title} ({year}) | id=`{item.get('id')}` | doi={doi}")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = {"path": output.as_posix(), "items_written": min(len(pending), args.limit)}
    append_run_log({"type": "paper_review_report", "timestamp": utc_now(), "result": result})
    print(json.dumps(result, indent=2, sort_keys=True))


def command_clean_notes(_: argparse.Namespace) -> None:
    queue = load_queue()
    updated = 0
    for item in queue["items"]:
        if not item.get("imported"):
            continue
        notes = item.get("notes", [])
        cleaned = [note for note in notes if not note.startswith("Pending retry after")]
        if cleaned != notes:
            item["notes"] = cleaned
            updated += 1
    save_queue(queue)
    result = {"imported_items_cleaned": updated}
    append_run_log({"type": "clean_notes", "timestamp": utc_now(), "result": result})
    print(json.dumps(result, indent=2, sort_keys=True))


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import helper for the knowledge base")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-db", help="Initialize JSONDB files")
    init_parser.set_defaults(func=command_init_db)

    wiki_parser = subparsers.add_parser("import-wikipedia", help="Import Wikipedia summaries for term inventory")
    wiki_parser.add_argument("--limit", type=int, default=None, help="Maximum terms to import")
    wiki_parser.add_argument("--link-limit", type=int, default=25, help="Linked articles to queue per imported article")
    wiki_parser.add_argument("--sleep", type=float, default=WIKIMEDIA_DEFAULT_SLEEP_SECONDS, help="Delay between requests")
    wiki_parser.add_argument("--no-progress", action="store_true", help="Disable per-item progress logs on stderr")
    wiki_parser.set_defaults(func=command_import_wikipedia)

    queued_wiki_parser = subparsers.add_parser("import-queued-wikipedia", help="Import pending linked Wikipedia summaries from the queue")
    queued_wiki_parser.add_argument("--limit", type=int, default=25, help="Maximum queued linked articles to import")
    queued_wiki_parser.add_argument("--link-limit", type=int, default=0, help="Linked articles to queue per imported article")
    queued_wiki_parser.add_argument("--sleep", type=float, default=WIKIMEDIA_DEFAULT_SLEEP_SECONDS, help="Delay between requests")
    queued_wiki_parser.add_argument("--no-progress", action="store_true", help="Disable per-item progress logs on stderr")
    queued_wiki_parser.set_defaults(func=command_import_queued_wikipedia)

    paper_metadata_parser = subparsers.add_parser("import-paper-metadata", help="Import Crossref metadata cards for queued paper references")
    paper_metadata_parser.add_argument("--limit", type=int, default=25, help="Maximum queued DOI references to import")
    paper_metadata_parser.add_argument("--sleep", type=float, default=0.2, help="Delay between requests")
    paper_metadata_parser.set_defaults(func=command_import_paper_metadata)

    paper_manual_parser = subparsers.add_parser("import-paper-manual-matches", help="Import only manually curated paper mappings")
    paper_manual_parser.add_argument("--sleep", type=float, default=0.0, help="Delay between requests")
    paper_manual_parser.set_defaults(func=command_import_paper_manual_matches)

    crossref_parser = subparsers.add_parser("queue-crossref-references", help="Queue Crossref references from source DOI metadata")
    crossref_parser.add_argument("--limit", type=int, default=None, help="Maximum source DOI records to inspect")
    crossref_parser.add_argument("--sleep", type=float, default=0.2, help="Delay between requests")
    crossref_parser.set_defaults(func=command_queue_crossref)

    wiki_terms_parser = subparsers.add_parser("queue-wikipedia-terms", help="Queue all curated Wikipedia search terms")
    wiki_terms_parser.set_defaults(func=command_queue_wikipedia_terms)

    run_parser = subparsers.add_parser("run-initial", help="Run Wikipedia import and Crossref reference queueing")
    run_parser.add_argument("--wiki-limit", type=int, default=40, help="Maximum term inventory records to import")
    run_parser.add_argument("--reference-limit", type=int, default=20, help="Maximum source DOI records to inspect")
    run_parser.add_argument("--link-limit", type=int, default=25, help="Linked articles to queue per imported article")
    run_parser.add_argument("--sleep", type=float, default=WIKIMEDIA_DEFAULT_SLEEP_SECONDS, help="Delay between requests")
    run_parser.add_argument("--no-progress", action="store_true", help="Disable per-item progress logs on stderr")
    run_parser.set_defaults(func=command_run_initial)

    clear_errors_parser = subparsers.add_parser("clear-errors", help="Remove import_error queue entries")
    clear_errors_parser.set_defaults(func=command_clear_errors)

    sync_wiki_terms_parser = subparsers.add_parser("sync-wikipedia-terms", help="Mark term records imported when matching article summaries exist")
    sync_wiki_terms_parser.set_defaults(func=command_sync_wikipedia_terms)

    wiki_review_parser = subparsers.add_parser("apply-wiki-review", help="Apply rejected Wikipedia mapping review decisions")
    wiki_review_parser.set_defaults(func=command_apply_wiki_review)

    paper_review_parser = subparsers.add_parser("apply-paper-review", help="Apply paper review decisions for deferred or rejected items")
    paper_review_parser.set_defaults(func=command_apply_paper_review)

    paper_review_report_parser = subparsers.add_parser("paper-review-report", help="Write a Markdown report for unresolved paper references")
    paper_review_report_parser.add_argument("--limit", type=int, default=200, help="Maximum pending items to write")
    paper_review_report_parser.add_argument(
        "--output",
        default="kb/research/paper_review_queue.md",
        help="Output Markdown path",
    )
    paper_review_report_parser.set_defaults(func=command_paper_review_report)

    clean_notes_parser = subparsers.add_parser("clean-notes", help="Clean stale retry notes from imported queue records")
    clean_notes_parser.set_defaults(func=command_clean_notes)

    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
