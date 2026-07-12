#!/usr/bin/env python3
"""Validate Creative Style Kit v1 schemas and a cross-linked record bundle."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ModuleNotFoundError as exc:  # pragma: no cover - exercised only in an unprepared environment
    raise SystemExit(
        "Style Kit contract validation requires jsonschema; "
        "install optional dependencies with `python3 -m pip install -r requirements-dev.txt`."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_DIR = ROOT / "schemas" / "style_kit" / "v1"
DEFAULT_BUNDLE = DEFAULT_SCHEMA_DIR / "examples" / "valid-contract-bundle.json"
SCHEMA_FILES = {
    "sources": "source.schema.json",
    "observations": "observation.schema.json",
    "generation_guidance": "generation-guidance.schema.json",
    "pilot_runs": "pilot-run.schema.json",
    "evaluation_events": "evaluation-event.schema.json",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def context_sha256(run: dict[str, Any]) -> str:
    personalized = next(
        (variant for variant in run.get("variants", []) if variant.get("kind") == "personalized"),
        {},
    )
    context = {
        "guidance_refs": personalized.get("guidance_refs", []),
        "profile_atom_refs": personalized.get("profile_atom_refs", []),
        "source_refs": run.get("source_refs", []),
    }
    encoded = json.dumps(context, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def schema_errors(bundle: dict[str, Any], schema_dir: Path) -> list[str]:
    errors: list[str] = []
    if bundle.get("bundle_version") != "sol.style-kit.contract-bundle.v1":
        errors.append("bundle_version must be sol.style-kit.contract-bundle.v1")

    for collection, filename in SCHEMA_FILES.items():
        records = bundle.get(collection)
        if not isinstance(records, list):
            errors.append(f"{collection} must be an array")
            continue
        schema = load_json(schema_dir / filename)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # jsonschema reports the exact schema path in its message
            errors.append(f"schema {filename} is invalid: {exc}")
            continue
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for index, record in enumerate(records):
            for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
                field_path = ".".join(str(part) for part in error.path) or "<record>"
                errors.append(f"{collection}[{index}].{field_path}: {error.message}")
    return errors


def index_records(records: list[dict[str, Any]], collection: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record.get("id")
        if not isinstance(record_id, str):
            continue
        if record_id in indexed:
            errors.append(f"{collection} contains duplicate id {record_id}")
        indexed[record_id] = record
    return indexed


def validate_record_lifecycle(record: dict[str, Any], label: str, errors: list[str]) -> None:
    state = record.get("record_state")
    deleted_at = record.get("deleted_at")
    export_state = record.get("export_state")
    if state == "active" and deleted_at is not None:
        errors.append(f"{label} is active but has deleted_at")
    if state == "active" and export_state != "exportable":
        errors.append(f"{label} is active but is not exportable")
    if state == "deleted" and not deleted_at:
        errors.append(f"{label} is deleted but has no deleted_at")
    if state == "deleted" and export_state != "deleted":
        errors.append(f"{label} is deleted but export_state is not deleted")


def validate_timestamps(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            field = f"{label}.{key}"
            if key.endswith("_at") and nested is not None:
                try:
                    parsed = datetime.fromisoformat(nested.replace("Z", "+00:00"))
                except (AttributeError, TypeError, ValueError):
                    errors.append(f"{field} must be a timezone-aware UTC timestamp")
                    continue
                if parsed.tzinfo is None or parsed.astimezone(timezone.utc).utcoffset() != parsed.utcoffset():
                    errors.append(f"{field} must be a timezone-aware UTC timestamp")
            else:
                validate_timestamps(nested, field, errors)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            validate_timestamps(nested, f"{label}[{index}]", errors)


def validate_cross_record_contracts(bundle: dict[str, Any], allow_external: bool = False) -> list[str]:
    errors: list[str] = []
    collections = {
        name: records if isinstance(records := bundle.get(name), list) else []
        for name in SCHEMA_FILES
    }
    sources = index_records(collections["sources"], "sources", errors)
    observations = index_records(collections["observations"], "observations", errors)
    guidance = index_records(collections["generation_guidance"], "generation_guidance", errors)
    runs = index_records(collections["pilot_runs"], "pilot_runs", errors)
    index_records(collections["evaluation_events"], "evaluation_events", errors)
    consent_to_source = {
        source.get("consent", {}).get("consent_id"): source
        for source in sources.values()
        if source.get("consent", {}).get("consent_id")
    }

    for source_id, source in sources.items():
        validate_timestamps(source, source_id, errors)
        validate_record_lifecycle(source, source_id, errors)
        content = source.get("content")
        checksum = source.get("content_sha256")
        if source.get("record_state") == "active":
            if not content or not checksum:
                errors.append(f"{source_id} must retain content and checksum while active")
            elif sha256_text(content) != checksum:
                errors.append(f"{source_id} content_sha256 does not match content")
        elif content is not None or checksum is not None:
            errors.append(f"{source_id} must remove content and checksum when deleted")

    for observation_id, observation in observations.items():
        validate_timestamps(observation, observation_id, errors)
        validate_record_lifecycle(observation, observation_id, errors)
        source = sources.get(observation.get("source_id"))
        if source is None:
            errors.append(f"{observation_id} references unknown source {observation.get('source_id')}")
            continue
        if observation.get("owner_id") != source.get("owner_id"):
            errors.append(f"{observation_id} owner does not match its source")
        if observation.get("consent_ref") != source.get("consent", {}).get("consent_id"):
            errors.append(f"{observation_id} consent_ref does not match its source consent")
        if "profile_observation" not in source.get("consent", {}).get("allowed_uses", []):
            errors.append(f"{observation_id} source consent does not allow profile observation")
        if source.get("record_state") == "deleted" and observation.get("review_state") != "invalidated":
            errors.append(f"{observation_id} must be invalidated when its source is deleted")
        evidence = observation.get("evidence", {})
        excerpt = evidence.get("excerpt")
        start = evidence.get("character_start")
        end = evidence.get("character_end")
        content = source.get("content")
        if content is not None and excerpt is not None and isinstance(start, int) and isinstance(end, int):
            if start > end or content[start:end] != excerpt:
                errors.append(f"{observation_id} evidence location does not match its source excerpt")

    for guidance_id, item in guidance.items():
        validate_timestamps(item, guidance_id, errors)
        validate_record_lifecycle(item, guidance_id, errors)
        if not item.get("observation_refs") and not item.get("profile_atom_refs"):
            errors.append(f"{guidance_id} must reference an observation or profile atom")
        for source_ref in item.get("source_refs", []):
            source = sources.get(source_ref)
            if source is None:
                errors.append(f"{guidance_id} references unknown source {source_ref}")
            elif source.get("owner_id") != item.get("owner_id"):
                errors.append(f"{guidance_id} owner does not match source {source_ref}")
            else:
                consent = source.get("consent", {})
                if consent.get("consent_id") not in item.get("consent_refs", []):
                    errors.append(f"{guidance_id} does not carry source consent for {source_ref}")
                if "style_guidance" not in consent.get("allowed_uses", []):
                    errors.append(f"{guidance_id} source consent does not allow style guidance")
                if source.get("record_state") == "deleted" and item.get("user_state") != "disabled":
                    errors.append(f"{guidance_id} must be disabled when source {source_ref} is deleted")
        for observation_ref in item.get("observation_refs", []):
            observation = observations.get(observation_ref)
            if observation is None:
                errors.append(f"{guidance_id} references unknown observation {observation_ref}")
            elif observation.get("owner_id") != item.get("owner_id"):
                errors.append(f"{guidance_id} owner does not match observation {observation_ref}")
        for consent_ref in item.get("consent_refs", []):
            if consent_ref not in consent_to_source:
                errors.append(f"{guidance_id} references unknown consent {consent_ref}")

    for run_id, run in runs.items():
        validate_timestamps(run, run_id, errors)
        validate_record_lifecycle(run, run_id, errors)
        mode = run.get("mode")
        provider_uri = run.get("provider", {}).get("uri", "")
        if mode == "dry_run" and not provider_uri.startswith("dry-run://"):
            errors.append(f"{run_id} dry_run mode requires a dry-run:// provider URI")
        if mode == "mock" and not provider_uri.startswith("mock://"):
            errors.append(f"{run_id} mock mode requires a mock:// provider URI")
        if mode in {"dry_run", "mock"} and run.get("external_provider_consent") is not False:
            errors.append(f"{run_id} local mode must not claim external-provider consent")
        if mode == "external":
            if not allow_external:
                errors.append(f"{run_id} external mode is not approved")
            if run.get("external_provider_consent") is not True:
                errors.append(f"{run_id} external mode requires explicit provider consent")
        for source_ref in run.get("source_refs", []):
            source = sources.get(source_ref)
            if source is None:
                errors.append(f"{run_id} references unknown source {source_ref}")
            elif source.get("owner_id") != run.get("owner_id"):
                errors.append(f"{run_id} owner does not match source {source_ref}")
            else:
                consent = source.get("consent", {})
                if consent.get("consent_id") not in run.get("consent_refs", []):
                    errors.append(f"{run_id} does not carry source consent for {source_ref}")
                if "local_generation" not in consent.get("allowed_uses", []):
                    errors.append(f"{run_id} source consent does not allow local generation")
                if mode == "external" and consent.get("external_provider_allowed") is not True:
                    errors.append(f"{run_id} source consent forbids external provider use")
        for consent_ref in run.get("consent_refs", []):
            if consent_ref not in consent_to_source:
                errors.append(f"{run_id} references unknown consent {consent_ref}")
        variants = run.get("variants", [])
        kinds = [variant.get("kind") for variant in variants]
        if sorted(kinds) != ["generic", "personalized"]:
            errors.append(f"{run_id} must contain one generic and one personalized variant")
        for variant in variants:
            label = f"{run_id}/{variant.get('variant_id', '<variant>')}"
            if variant.get("kind") == "generic" and (
                variant.get("guidance_refs") or variant.get("profile_atom_refs")
            ):
                errors.append(f"{label} generic variant must not contain personalization references")
            if variant.get("kind") == "personalized":
                for guidance_ref in variant.get("guidance_refs", []):
                    item = guidance.get(guidance_ref)
                    if item is None:
                        errors.append(f"{label} references unknown guidance {guidance_ref}")
                    elif item.get("user_state") not in {"confirmed", "edited"}:
                        errors.append(f"{label} references guidance that is not user-approved: {guidance_ref}")
                    elif item.get("record_state") != "active":
                        errors.append(f"{label} references inactive guidance {guidance_ref}")
            output = variant.get("output")
            output_checksum = variant.get("output_sha256")
            if output is not None and sha256_text(output) != output_checksum:
                errors.append(f"{label} output_sha256 does not match output")
            if output is None and output_checksum is not None:
                errors.append(f"{label} has an output checksum without output")
        if run.get("context_sha256") != context_sha256(run):
            errors.append(f"{run_id} context_sha256 does not match exact run references")

    for event in collections["evaluation_events"]:
        event_id = event.get("id", "<evaluation>")
        validate_timestamps(event, event_id, errors)
        validate_record_lifecycle(event, event_id, errors)
        run = runs.get(event.get("run_id"))
        if run is None:
            errors.append(f"{event_id} references unknown run {event.get('run_id')}")
            continue
        if event.get("owner_id") != run.get("owner_id"):
            errors.append(f"{event_id} owner does not match its run")
        for consent_ref in event.get("consent_refs", []):
            source = consent_to_source.get(consent_ref)
            if source is None:
                errors.append(f"{event_id} references unknown consent {consent_ref}")
            elif "product_evaluation" not in source.get("consent", {}).get("allowed_uses", []):
                errors.append(f"{event_id} source consent does not allow product evaluation")
        personalized = next(
            (variant for variant in run.get("variants", []) if variant.get("kind") == "personalized"),
            {},
        )
        used_guidance = set(personalized.get("guidance_refs", []))
        unknown_guidance = set(event.get("affected_guidance_refs", [])) - used_guidance
        if unknown_guidance:
            errors.append(f"{event_id} references guidance not used by its run: {sorted(unknown_guidance)}")
        if set(event.get("labels", [])) & {"too_strong", "too_generic", "wrong"} and not event.get("correction"):
            errors.append(f"{event_id} negative feedback requires a correction")
    return errors


def validate_contract_bundle(
    bundle: dict[str, Any],
    schema_dir: Path = DEFAULT_SCHEMA_DIR,
    allow_external: bool = False,
) -> list[str]:
    return schema_errors(bundle, schema_dir) + validate_cross_record_contracts(bundle, allow_external)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Creative Style Kit v1 record contracts.")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR)
    parser.add_argument("--allow-external", action="store_true", help="Schema exercise only; not product approval.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bundle = load_json(args.bundle)
    errors = validate_contract_bundle(bundle, args.schema_dir, args.allow_external)
    result = {"bundle": args.bundle.as_posix(), "error_count": len(errors), "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
