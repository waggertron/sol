#!/usr/bin/env python3
"""Validate the experimental Sol OCEAN candidate without activating it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(".")
DEFAULT_CANDIDATE = ROOT / "assessments" / "ocean" / "experimental" / "sol_ocean_quick_v0.json"
STORED_INSTRUMENTS = ROOT / "assessments" / "ocean" / "instruments"
EXPECTED_DOMAINS = {"openness", "conscientiousness", "extraversion", "agreeableness", "emotional_stability"}
REQUIRED_ITEM_FIELDS = {
    "id",
    "source_order",
    "domain",
    "subconstruct",
    "text",
    "keyed",
    "blueprint_ref",
    "sensitivity_level",
    "reading_level_target",
    "expected_failure_modes",
    "design_provenance",
}
BLOCKED_ITEM_TERMS = {
    "diagnosis",
    "disorder",
    "intelligence",
    "employability",
    "protected class",
    "mental illness",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", value.lower())).strip()


def instrument_items(instrument: dict[str, Any]) -> list[dict[str, Any]]:
    if instrument.get("items"):
        return list(instrument["items"])
    return [item for scale in instrument.get("scales", []) for item in scale.get("items", [])]


def stored_item_texts(instruments_dir: Path = STORED_INSTRUMENTS) -> set[str]:
    texts: set[str] = set()
    for path in sorted(instruments_dir.glob("*.json")):
        for item in instrument_items(load_json(path)):
            if item.get("text"):
                texts.add(normalized_text(item["text"]))
    return texts


def validate_candidate(candidate: dict[str, Any], comparison_texts: set[str]) -> list[str]:
    errors: list[str] = []
    items = candidate.get("items", [])
    scales = candidate.get("scales", [])

    if candidate.get("administration_status") != "experimental_design_review_only":
        errors.append("candidate must remain experimental_design_review_only")
    if candidate.get("scoring", {}).get("product_profile_atom_output_enabled") is not False:
        errors.append("product profile atom output must be disabled")
    if len(items) != 30:
        errors.append("candidate must contain exactly 30 items")

    ids = [item.get("id") for item in items]
    orders = [item.get("source_order") for item in items]
    texts = [normalized_text(item.get("text", "")) for item in items]
    if len(set(ids)) != len(ids):
        errors.append("item ids must be unique")
    if sorted(orders) != list(range(1, 31)):
        errors.append("source_order must contain each integer from 1 through 30")
    if len(set(texts)) != len(texts):
        errors.append("candidate item texts must be unique after normalization")

    domain_items: dict[str, list[dict[str, Any]]] = {}
    subconstruct_items: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for index, item in enumerate(items, start=1):
        missing = sorted(REQUIRED_ITEM_FIELDS - set(item))
        if missing:
            errors.append(f"item {index} missing fields: {', '.join(missing)}")
            continue
        domain = item["domain"]
        domain_items.setdefault(domain, []).append(item)
        subconstruct_items.setdefault((domain, item["subconstruct"]), []).append(item)
        if item["keyed"] not in {"positive", "negative"}:
            errors.append(f"item {item['id']} has invalid keying")
        if item["sensitivity_level"] not in {"low", "medium"}:
            errors.append(f"item {item['id']} has invalid sensitivity")
        if not item["expected_failure_modes"]:
            errors.append(f"item {item['id']} must name an expected failure mode")
        if normalized_text(item["text"]) in comparison_texts:
            errors.append(f"item {item['id']} exactly collides with stored instrument wording")
        lowered = item["text"].lower()
        for term in BLOCKED_ITEM_TERMS:
            if term in lowered:
                errors.append(f"item {item['id']} contains blocked term `{term}`")

    if set(domain_items) != EXPECTED_DOMAINS:
        errors.append("candidate must cover exactly the five expected OCEAN domains")
    for domain in EXPECTED_DOMAINS:
        if len(domain_items.get(domain, [])) != 6:
            errors.append(f"domain {domain} must contain exactly six items")
    if len(subconstruct_items) != 15:
        errors.append("candidate must contain exactly 15 domain/subconstruct pairs")
    for (domain, subconstruct), pair in subconstruct_items.items():
        if len(pair) != 2 or {item["keyed"] for item in pair} != {"positive", "negative"}:
            errors.append(f"{domain}.{subconstruct} must have one positive and one negative item")

    item_ids = set(ids)
    scale_refs = [item_ref for scale in scales for item_ref in scale.get("item_refs", [])]
    if len(scales) != 5 or {scale.get("domain") for scale in scales} != EXPECTED_DOMAINS:
        errors.append("candidate must contain one scale for each expected domain")
    if len(scale_refs) != len(set(scale_refs)) or set(scale_refs) != item_ids:
        errors.append("scale item_refs must cover every item exactly once")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the experimental Sol OCEAN candidate.")
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidate = load_json(args.candidate)
    errors = validate_candidate(candidate, stored_item_texts())
    result = {"candidate": args.candidate.as_posix(), "error_count": len(errors), "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

