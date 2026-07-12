#!/usr/bin/env python3
"""Generate assessment-derived profile atom candidates from stored instruments."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")


@dataclass
class ResponseScale:
    min_value: float
    max_value: float


def response_scale_bounds(instrument: dict[str, Any]) -> ResponseScale:
    values = [entry["value"] for entry in instrument["response_scale"]["values"]]
    return ResponseScale(min_value=min(values), max_value=max(values))


def reverse_score(value: float, scale: ResponseScale) -> float:
    return scale.min_value + scale.max_value - value


def normalize_score(value: float, minimum: float, maximum: float) -> float:
    if maximum <= minimum:
        return 0.5
    return max(0.0, min(1.0, (value - minimum) / (maximum - minimum)))


def label_band(normalized: float) -> str:
    if normalized >= 0.8:
        return "relatively high"
    if normalized >= 0.6:
        return "moderately elevated"
    if normalized > 0.4:
        return "mid-range"
    if normalized > 0.2:
        return "moderately low"
    return "relatively low"


def canonical_domain(domain: str) -> str:
    if domain == "emotional_stability":
        return "neuroticism"
    return domain


def user_facing_domain(domain: str) -> str:
    if domain == "emotional_stability":
        return "emotional stability"
    return domain.replace("_", " ")


def claim_for_domain(domain: str, normalized: float) -> str:
    band = label_band(normalized)
    display = user_facing_domain(domain)
    if domain == "emotional_stability":
        return (
            f"User self-report suggests {band} emotional stability on this instrument. "
            "Treat as provisional self-report evidence, not a diagnostic conclusion."
        )
    if domain == "neuroticism":
        return (
            f"User self-report suggests {band} neuroticism or emotional reactivity on this instrument. "
            "Treat as provisional self-report evidence, not a diagnostic conclusion."
        )
    return (
        f"User self-report suggests {band} {display} on this instrument. "
        "Treat as provisional self-report evidence, not a fixed identity claim."
    )


def confidence_for_scale(scale: dict[str, Any], item_count: int) -> float:
    alpha = scale.get("reliability_alpha")
    if isinstance(alpha, (int, float)):
        if alpha >= 0.8:
            return 0.8
        if alpha >= 0.7:
            return 0.72
        if alpha >= 0.6:
            return 0.64
        return 0.58
    if item_count >= 8:
        return 0.68
    if item_count >= 4:
        return 0.62
    return 0.52


def uncertainty_note(instrument: dict[str, Any], scored: dict[str, Any]) -> str:
    if instrument.get("id") == "tipi":
        return (
            "TIPI is intentionally very brief. Treat this result as a low-resolution "
            "self-report snapshot with diminished precision, not a fixed identity claim."
        )
    alpha = scored.get("reliability_alpha")
    if alpha is not None:
        return (
            f"This scale reports reliability alpha {alpha:.2f}. Reliability describes "
            "score consistency in prior measurement work; it does not prove this claim "
            "is true for this person or context."
        )
    return "Treat this score as provisional self-report evidence that may vary by context and time."


def inline_items_for_scale(instrument: dict[str, Any], scale: dict[str, Any]) -> list[dict[str, Any]]:
    if "items" in scale:
        return list(scale["items"])
    item_index = {item["id"]: item for item in instrument.get("items", [])}
    return [item_index[item_ref] for item_ref in scale.get("item_refs", [])]


def parse_responses(path: Path) -> dict[str, float]:
    raw = load_json(path)
    if isinstance(raw, dict):
        return {str(key): float(value) for key, value in raw.items()}
    if isinstance(raw, list):
        parsed: dict[str, float] = {}
        for entry in raw:
            if not isinstance(entry, dict):
                raise ValueError("List response entries must be objects.")
            item_id = entry.get("item_id") or entry.get("id")
            if item_id is None:
                raise ValueError("Response entry missing item_id.")
            parsed[str(item_id)] = float(entry["value"])
        return parsed
    raise ValueError("Responses JSON must be an object or a list of objects.")


def collect_response_value(
    item: dict[str, Any],
    responses: dict[str, float],
    source_order_index: dict[int, str],
) -> float:
    item_id = item["id"]
    if item_id in responses:
        return responses[item_id]
    order = item.get("source_order")
    if order is not None and str(order) in responses:
        return responses[str(order)]
    if order is not None and order in source_order_index:
        mapped_id = source_order_index[order]
        if mapped_id in responses:
            return responses[mapped_id]
    raise KeyError(f"Missing response for item {item_id}")


def score_scale(
    instrument: dict[str, Any],
    scale: dict[str, Any],
    responses: dict[str, float],
    resp_scale: ResponseScale,
) -> dict[str, Any]:
    items = inline_items_for_scale(instrument, scale)
    source_order_index = {item.get("source_order"): item["id"] for item in items if item.get("source_order") is not None}
    keyed_scores: list[float] = []
    evidence_lines: list[str] = []
    item_evidence: list[dict[str, Any]] = []
    raw_values: list[float] = []

    for item in items:
        value = collect_response_value(item, responses, source_order_index)
        raw_values.append(value)
        keyed = reverse_score(value, resp_scale) if item.get("keyed") == "negative" else value
        keyed_scores.append(keyed)
        item_evidence.append(
            {
                "item_id": item["id"],
                "item_text": item.get("text"),
                "response_value": value,
                "keying": item.get("keyed", "positive"),
                "reverse_scored": item.get("keyed") == "negative",
                "keyed_value": keyed,
            }
        )
        evidence_lines.append(
            f"{item['id']}={value:g} ({'reverse-keyed' if item.get('keyed') == 'negative' else 'positive-keyed'})"
        )

    method = instrument["scoring"]["method"]
    if method == "sum_keyed_items":
        raw_score = sum(keyed_scores)
        score_min = resp_scale.min_value * len(items)
        score_max = resp_scale.max_value * len(items)
    elif method == "average_two_items_per_domain":
        raw_score = sum(keyed_scores) / len(keyed_scores)
        score_min = resp_scale.min_value
        score_max = resp_scale.max_value
    else:
        raise ValueError(f"Unsupported scoring method: {method}")

    normalized = normalize_score(raw_score, score_min, score_max)
    return {
        "scale_id": scale["id"],
        "label": scale.get("label") or scale["id"],
        "domain": scale.get("domain") or "unknown",
        "raw_score": raw_score,
        "score_min": score_min,
        "score_max": score_max,
        "normalized_score": normalized,
        "item_count": len(items),
        "raw_responses": raw_values,
        "item_evidence": item_evidence,
        "evidence_lines": evidence_lines,
        "reliability_alpha": scale.get("reliability_alpha"),
        "scoring_method": method,
        "score_interpretation": instrument.get("scoring", {}).get("score_interpretation"),
    }


def build_profile_atom(
    instrument: dict[str, Any],
    session_id: str,
    completed_at: str,
    scored: dict[str, Any],
) -> dict[str, Any]:
    domain = canonical_domain(scored["domain"])
    normalized = scored["normalized_score"]
    instrument_id = instrument["id"]
    scale_slug = slugify(scored["scale_id"])
    confidence = confidence_for_scale({"reliability_alpha": scored.get("reliability_alpha")}, scored["item_count"])
    evidence = [
        f"Self-report assessment score from instrument `{instrument_id}` scale `{scored['scale_id']}`.",
        f"Raw score {scored['raw_score']:.2f} on range [{scored['score_min']:.2f}, {scored['score_max']:.2f}] normalized to {normalized:.2f}.",
        *scored["evidence_lines"],
    ]
    claim = claim_for_domain(scored["domain"], normalized)
    return {
        "id": f"assessment.{instrument_id}.{scale_slug}.v0",
        "label": f"{scored['label']} self-report tendency",
        "domain": "stable_trait_tendencies",
        "original_claim": claim,
        "claim": claim,
        "state": "provisional_atom",
        "activation_scope": "review_only",
        "evidence": evidence,
        "source_ids": [
            f"assessment:{instrument_id}",
            f"assessment_session:{session_id}",
            f"assessment_scale:{scored['scale_id']}",
        ],
        "data_modality": ["assessment"],
        "context": ["general_self_report"],
        "confidence": round(confidence, 2),
        "stability": "high",
        "recency": completed_at,
        "sensitivity_level": "low" if domain != "neuroticism" else "medium",
        "user_visibility": "visible_editable",
        "user_feedback": "unconfirmed",
        "user_note": "",
        "review_history": [],
        "generation_mappings": [],
        "generation_mapping_notes": [],
        "counterevidence": [],
        "last_updated": completed_at,
        "assessment_metadata": {
            "assessment_id": instrument_id,
            "assessment_name": instrument["name"],
            "assessment_family": instrument.get("family"),
            "construct_system": instrument.get("construct_system"),
            "scale_id": scored["scale_id"],
            "scale_label": scored["label"],
            "trait": domain,
            "score_type": instrument["scoring"]["method"],
            "score_value": round(scored["raw_score"], 4),
            "score_range": [scored["score_min"], scored["score_max"]],
            "normalized_score": round(normalized, 4),
            "reliability_alpha": scored.get("reliability_alpha"),
            "scoring_method": scored.get("scoring_method"),
            "score_interpretation": scored.get("score_interpretation"),
            "item_evidence": scored.get("item_evidence", []),
            "uncertainty_note": uncertainty_note(instrument, scored),
            "instrument_notes": instrument.get("notes", []),
            "license_status": instrument.get("license", {}).get("status"),
            "source_publisher": instrument.get("source", {}).get("publisher"),
            "source_url": instrument.get("source", {}).get("url"),
            "session_id": session_id,
        },
    }


def generate_output(instrument: dict[str, Any], responses: dict[str, float], session_id: str, completed_at: str) -> dict[str, Any]:
    resp_scale = response_scale_bounds(instrument)
    scores = [score_scale(instrument, scale, responses, resp_scale) for scale in instrument["scales"]]
    atoms = [build_profile_atom(instrument, session_id, completed_at, score) for score in scores]
    return {
        "assessment_id": instrument["id"],
        "assessment_name": instrument["name"],
        "session_id": session_id,
        "completed_at": completed_at,
        "scores": scores,
        "profile_atoms": atoms,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate assessment-derived profile atom candidates.")
    parser.add_argument("--instrument", type=Path, required=True, help="Path to an assessment instrument JSON file.")
    parser.add_argument("--responses", type=Path, required=True, help="Path to JSON responses keyed by item id or source order.")
    parser.add_argument("--session-id", required=True, help="Assessment session identifier.")
    parser.add_argument("--completed-at", required=True, help="Completion timestamp to stamp onto derived atoms.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    instrument = load_json(args.instrument)
    responses = parse_responses(args.responses)
    output = generate_output(instrument, responses, args.session_id, args.completed_at)
    print(save_json(output), end="")


if __name__ == "__main__":
    main()
