#!/usr/bin/env python3
"""Import helper for the personality knowledge base.

The importer keeps a JSONDB queue of discovered sources and imports Wikipedia
article summaries as attributed Markdown cards. It intentionally avoids full
article dumps by default because this repository is public.
"""

from __future__ import annotations

import argparse
import json
import re
import time
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
WIKI_IMPORTS = ROOT / "kb" / "wiki_imports"
SOURCES_DIR = ROOT / "sources"
USER_AGENT = "sol-personality-rag/0.1 (research import; contact: local)"


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


def request_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def ensure_db() -> None:
    JSONDB.mkdir(parents=True, exist_ok=True)
    WIKI_IMPORTS.mkdir(parents=True, exist_ok=True)
    if not IMPORT_QUEUE.exists():
        save_json(IMPORT_QUEUE, {"version": 1, "items": []})
    if not IMPORT_RUNS.exists():
        save_json(IMPORT_RUNS, {"version": 1, "runs": []})


def load_queue() -> dict[str, Any]:
    ensure_db()
    return load_json(IMPORT_QUEUE, {"version": 1, "items": []})


def save_queue(queue: dict[str, Any]) -> None:
    save_json(IMPORT_QUEUE, queue)


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
    return doi


def doi_url(doi: str) -> str:
    return f"https://doi.org/{normalize_doi(doi)}"


def crossref_work(doi: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(normalize_doi(doi), safe="")
    return request_json(f"https://api.crossref.org/works/{encoded}")["message"]


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
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": term,
            "gsrlimit": 1,
            "prop": "extracts|links|info",
            "exintro": 1,
            "explaintext": 1,
            "inprop": "url",
            "pllimit": min(link_limit, 50),
            "format": "json",
            "utf8": 1,
        }
    )
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


def write_wiki_card(term: str, domain: str, summary: dict[str, Any]) -> Path:
    title = summary.get("title") or term
    page_url = summary.get("content_urls", {}).get("desktop", {}).get("page") or summary.get("canonicalurl")
    extract = summary.get("extract") or ""
    description = summary.get("description") or ""
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


def import_wikipedia(limit: int | None = None, link_limit: int = 25, sleep_seconds: float = 0.2) -> dict[str, int]:
    queue = load_queue()
    imported = 0
    skipped_existing = 0
    linked_added = 0
    errors = 0
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
        try:
            summary = wikipedia_page(term, link_limit=link_limit)
            if not summary:
                errors += 1
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
            time.sleep(sleep_seconds)
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
    result = {
        "terms_checked": len(terms),
        "summaries_imported": imported,
        "skipped_existing": skipped_existing,
        "linked_articles_added": linked_added,
        "errors": errors,
    }
    append_run_log({"type": "import_wikipedia", "timestamp": utc_now(), "result": result})
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
    result = import_wikipedia(limit=args.limit, link_limit=args.link_limit, sleep_seconds=args.sleep)
    print(json.dumps(result, indent=2, sort_keys=True))


def command_run_initial(args: argparse.Namespace) -> None:
    ensure_db()
    wiki_result = import_wikipedia(limit=args.wiki_limit, link_limit=args.link_limit, sleep_seconds=args.sleep)
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


def command_clean_notes(_: argparse.Namespace) -> None:
    queue = load_queue()
    updated = 0
    for item in queue["items"]:
        if not item.get("imported"):
            continue
        notes = item.get("notes", [])
        cleaned = [note for note in notes if not note.startswith("Pending retry after import error:")]
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
    wiki_parser.add_argument("--sleep", type=float, default=0.2, help="Delay between requests")
    wiki_parser.set_defaults(func=command_import_wikipedia)

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
    run_parser.add_argument("--sleep", type=float, default=0.2, help="Delay between requests")
    run_parser.set_defaults(func=command_run_initial)

    clear_errors_parser = subparsers.add_parser("clear-errors", help="Remove import_error queue entries")
    clear_errors_parser.set_defaults(func=command_clear_errors)

    sync_wiki_terms_parser = subparsers.add_parser("sync-wikipedia-terms", help="Mark term records imported when matching article summaries exist")
    sync_wiki_terms_parser.set_defaults(func=command_sync_wikipedia_terms)

    wiki_review_parser = subparsers.add_parser("apply-wiki-review", help="Apply rejected Wikipedia mapping review decisions")
    wiki_review_parser.set_defaults(func=command_apply_wiki_review)

    clean_notes_parser = subparsers.add_parser("clean-notes", help="Clean stale retry notes from imported queue records")
    clean_notes_parser.set_defaults(func=command_clean_notes)

    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
