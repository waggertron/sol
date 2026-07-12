#!/usr/bin/env python3
"""Local JSONDB-backed assessment session store for the assessment-first MVP."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
from typing import Any

from assessment_to_profile_atoms import generate_output, load_json, parse_responses


ROOT = Path(".")
JSONDB = ROOT / "jsondb"
SESSIONS_DB = JSONDB / "assessment_sessions.json"
SESSIONS_DB_ENV = "SOL_ASSESSMENT_SESSIONS_DB"
USER_FEEDBACK_VALUES = {"unconfirmed", "confirmed", "edited", "rejected"}
ATOM_STATE_VALUES = {"observed_candidate", "provisional_atom", "active_atom", "suppressed_atom"}
ACTIVATION_SCOPE_VALUES = {"review_only", "contextual", "global"}
GENERATION_FEEDBACK_VALUES = {"accurate", "useful", "too_strong", "too_generic", "wrong"}
NEGATIVE_GENERATION_FEEDBACK_VALUES = {"too_strong", "too_generic", "wrong"}
CONSENT_VERSION = "assessment-local-consent-v1"
MUTATION_LOCK = threading.RLock()


def serialized_mutation(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        with MUTATION_LOCK:
            return function(*args, **kwargs)

    return wrapped


def normalize_utc_timestamp(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp with timezone") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_generation_eligible(atom: dict[str, Any]) -> bool:
    return (
        atom.get("state") == "active_atom"
        and atom.get("activation_scope") in {"contextual", "global"}
        and atom.get("user_feedback") in {"confirmed", "edited"}
        and atom.get("sensitivity_level") != "blocked"
    )


def validate_atom_lifecycle(atom: dict[str, Any]) -> None:
    state = atom.get("state")
    scope = atom.get("activation_scope")
    feedback = atom.get("user_feedback")
    if state == "active_atom" and (
        scope not in {"contextual", "global"} or feedback not in {"confirmed", "edited"}
    ):
        raise ValueError("Active atoms require confirmed/edited feedback and contextual/global scope")
    if state in {"observed_candidate", "provisional_atom", "suppressed_atom"} and scope != "review_only":
        raise ValueError(f"{state} atoms must remain review_only")
    if feedback == "rejected" and (state != "suppressed_atom" or scope != "review_only"):
        raise ValueError("Rejected atoms must be suppressed and review_only")


def has_user_review(atom: dict[str, Any]) -> bool:
    return bool(
        atom.get("review_history")
        or atom.get("generation_mapping_notes")
        or atom.get("user_feedback") not in {None, "unconfirmed"}
        or atom.get("state") not in {None, "provisional_atom"}
        or atom.get("activation_scope") not in {None, "review_only"}
    )


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        temporary_path = Path(handle.name)
    try:
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def instrument_items(instrument: dict[str, Any]) -> list[dict[str, Any]]:
    if instrument.get("items"):
        return list(instrument["items"])
    return [item for scale in instrument.get("scales", []) for item in scale.get("items", [])]


def validate_response_map(instrument: dict[str, Any], responses: dict[str, float]) -> dict[str, float]:
    items = instrument_items(instrument)
    allowed_ids = {item["id"] for item in items}
    order_counts: dict[str, int] = {}
    for item in items:
        if item.get("source_order") is not None:
            key = str(item["source_order"])
            order_counts[key] = order_counts.get(key, 0) + 1
    unambiguous_order_ids = {
        str(item["source_order"]): item["id"]
        for item in items
        if item.get("source_order") is not None and order_counts[str(item["source_order"])] == 1
    }
    allowed_values = {float(entry["value"]) for entry in instrument["response_scale"]["values"]}
    raw = {str(key): float(value) for key, value in responses.items()}
    unknown = sorted(set(raw) - allowed_ids - set(unambiguous_order_ids))
    if unknown:
        raise ValueError(f"Unknown response item ids: {', '.join(unknown)}")
    normalized: dict[str, float] = {}
    for key, value in raw.items():
        item_id = unambiguous_order_ids.get(key, key)
        if item_id in normalized:
            raise ValueError(f"Duplicate response for item id: {item_id}")
        normalized[item_id] = value
    invalid = sorted(key for key, value in normalized.items() if value not in allowed_values)
    if invalid:
        raise ValueError(f"Responses outside the instrument scale: {', '.join(invalid)}")
    return normalized


def sessions_db_path() -> Path:
    configured = os.environ.get(SESSIONS_DB_ENV)
    if configured:
        return Path(configured)
    return SESSIONS_DB


def ensure_db() -> None:
    path = sessions_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        save_json(path, {"version": 1, "sessions": []})


def load_sessions() -> dict[str, Any]:
    ensure_db()
    return load_json(sessions_db_path())


def save_sessions(data: dict[str, Any]) -> None:
    save_json(sessions_db_path(), data)


def find_session(data: dict[str, Any], session_id: str) -> dict[str, Any] | None:
    for session in data["sessions"]:
        if session["session_id"] == session_id:
            return session
    return None


def summarize_session(session: dict[str, Any]) -> dict[str, Any]:
    atoms = session.get("profile_atoms", [])
    return {
        "session_id": session["session_id"],
        "user_id": session.get("user_id"),
        "instrument_id": session.get("instrument_id"),
        "instrument_name": session.get("instrument_name"),
        "status": session.get("status"),
        "started_at": session.get("started_at"),
        "completed_at": session.get("completed_at"),
        "response_count": len(session.get("responses", {})),
        "score_count": len(session.get("scores", [])),
        "profile_atom_count": len(atoms),
        "active_atom_count": sum(1 for atom in atoms if atom.get("state") == "active_atom"),
        "suppressed_atom_count": sum(1 for atom in atoms if atom.get("state") == "suppressed_atom"),
        "confirmed_atom_count": sum(1 for atom in atoms if atom.get("user_feedback") == "confirmed"),
        "rejected_atom_count": sum(1 for atom in atoms if atom.get("user_feedback") == "rejected"),
    }


def list_sessions() -> dict[str, Any]:
    data = load_sessions()
    summaries = [summarize_session(session) for session in data["sessions"]]
    summaries.sort(key=lambda session: session.get("started_at") or "", reverse=True)
    return {
        "version": data.get("version", 1),
        "session_count": len(summaries),
        "sessions": summaries,
    }


def list_profile_atoms() -> dict[str, Any]:
    data = load_sessions()
    records: list[dict[str, Any]] = []
    for session in data["sessions"]:
        summary = summarize_session(session)
        for atom in session.get("profile_atoms", []):
            records.append(
                {
                    **atom,
                    "session": summary,
                    "session_id": session["session_id"],
                    "instrument_id": session.get("instrument_id"),
                    "instrument_name": session.get("instrument_name"),
                }
            )
    records.sort(key=lambda atom: atom.get("last_updated") or atom.get("recency") or "", reverse=True)
    return {
        "atom_count": len(records),
        "atoms": records,
    }


def build_profile_context(generated_at: str, include_review_only: bool = False) -> dict[str, Any]:
    records = list_profile_atoms()["atoms"]
    selected: list[dict[str, Any]] = []
    for atom in records:
        rejected = atom.get("user_feedback") == "rejected"
        suppressed = atom.get("state") == "suppressed_atom"
        generation_eligible = is_generation_eligible(atom) and not rejected
        review_candidate = (
            include_review_only
            and atom.get("state") in {"observed_candidate", "provisional_atom"}
            and atom.get("activation_scope") == "review_only"
            and not rejected
        )
        if suppressed or not (generation_eligible or review_candidate):
            continue

        metadata = atom.get("assessment_metadata", {})
        selected.append(
            {
                "id": atom["id"],
                "session_id": atom.get("session_id"),
                "label": atom.get("label"),
                "domain": atom.get("domain"),
                "claim": atom.get("claim"),
                "state": atom.get("state"),
                "activation_scope": atom.get("activation_scope"),
                "eligible_for_generation": generation_eligible,
                "context": atom.get("context", []),
                "confidence": atom.get("confidence"),
                "evidence_summary": atom.get("evidence", []),
                "source_ids": atom.get("source_ids", []),
                "contraindications": atom.get("counterevidence", []),
                "generation_guidance": atom.get("generation_mappings", []),
                "generation_guidance_notes": atom.get("generation_mapping_notes", []),
                "uncertainty": {
                    "stability": atom.get("stability"),
                    "recency": atom.get("recency"),
                    "sensitivity_level": atom.get("sensitivity_level"),
                    "assessment_note": metadata.get("uncertainty_note"),
                },
                "user_feedback": atom.get("user_feedback"),
                "last_updated": atom.get("last_updated"),
            }
        )

    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "selection_policy": {
            "default": "confirmed/edited active contextual/global atoms with non-blocked sensitivity",
            "include_review_only": include_review_only,
            "review_only_atoms_are_generation_eligible": False,
        },
        "safety": {
            "intended_use": "user-reviewed personalization context",
            "prohibited_uses": [
                "diagnosis",
                "protected-class inference",
                "hidden profiling",
                "eligibility or high-impact decisions",
            ],
            "interpretation": "Claims are user-correctable evidence summaries, not identity facts.",
        },
        "atom_count": len(selected),
        "atoms": selected,
    }


@serialized_mutation
def record_generation_feedback(
    event_id: str,
    pilot_id: str,
    recorded_at: str,
    feedback: str,
    atom_refs: list[str],
    note: str = "",
) -> dict[str, Any]:
    if feedback not in GENERATION_FEEDBACK_VALUES:
        raise ValueError(f"Invalid generation feedback: {feedback}")
    if not event_id.strip() or not pilot_id.strip():
        raise ValueError("Feedback event id and pilot id are required")
    if not atom_refs:
        raise ValueError("At least one session_id::atom_id reference is required")
    if len(event_id) > 200 or len(pilot_id) > 200:
        raise ValueError("Feedback event id and pilot id must be 200 characters or fewer")
    if len(note) > 2000:
        raise ValueError("Feedback note must be 2000 characters or fewer")
    if feedback in NEGATIVE_GENERATION_FEEDBACK_VALUES and not note.strip():
        raise ValueError(f"Feedback note is required for `{feedback}`")
    if len(set(atom_refs)) != len(atom_refs):
        raise ValueError("Duplicate atom references are not allowed")

    data = load_sessions()
    events = data.setdefault("generation_feedback", [])
    if any(event.get("event_id") == event_id for event in events):
        raise ValueError(f"Generation feedback event already exists: {event_id}")

    matched: list[dict[str, Any]] = []
    for atom_ref in atom_refs:
        if "::" not in atom_ref:
            raise ValueError(f"Invalid atom reference: {atom_ref}")
        session_id, atom_id = atom_ref.split("::", 1)
        matches = [
            atom
            for session in data["sessions"]
            for atom in session.get("profile_atoms", [])
            if session.get("session_id") == session_id and atom.get("id") == atom_id
        ]
        if len(matches) != 1:
            raise ValueError(f"Expected one stored atom for feedback id `{atom_id}`, found {len(matches)}")
        atom = matches[0]
        if not is_generation_eligible(atom):
            raise ValueError(f"Atom is not generation-eligible: {atom_id}")
        matched.append(atom)

    recorded_at = normalize_utc_timestamp(recorded_at, "recorded_at")
    event = {
        "event_id": event_id,
        "pilot_id": pilot_id,
        "recorded_at": recorded_at,
        "feedback": feedback,
        "atom_refs": atom_refs,
        "note": note.strip(),
    }
    events.append(event)
    for atom in matched:
        atom.setdefault("generation_mapping_notes", []).append(
            {
                "feedback_event_id": event_id,
                "recorded_at": recorded_at,
                "feedback": feedback,
                "note": note.strip(),
            }
        )
        source_id = f"generation_feedback:{event_id}"
        if source_id not in atom.setdefault("source_ids", []):
            atom["source_ids"].append(source_id)
        atom["last_updated"] = recorded_at

    save_sessions(data)
    return event


@serialized_mutation
def create_session(
    session_id: str,
    instrument_path: str,
    started_at: str,
    consent_at: str,
    user_id: str | None = None,
    consent_version: str = CONSENT_VERSION,
) -> dict[str, Any]:
    data = load_sessions()
    if find_session(data, session_id):
        raise ValueError(f"Session already exists: {session_id}")

    instrument_file = Path(instrument_path)
    instrument = load_json(instrument_file)
    started_at = normalize_utc_timestamp(started_at, "started_at")
    consent_at = normalize_utc_timestamp(consent_at, "consent_at")
    if not consent_version.strip():
        raise ValueError("consent_version is required")
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "instrument_id": instrument["id"],
        "instrument_name": instrument["name"],
        "instrument_path": instrument_path,
        "instrument_schema_version": instrument.get("schema_version"),
        "instrument_sha256": hashlib.sha256(instrument_file.read_bytes()).hexdigest(),
        "scoring_method": instrument.get("scoring", {}).get("method"),
        "consent": {
            "acknowledged_at": consent_at,
            "version": consent_version,
            "scope": ["local_response_storage", "provisional_profile_atom_generation"],
        },
        "status": "in_progress",
        "started_at": started_at,
        "completed_at": None,
        "responses": {},
        "scores": [],
        "profile_atoms": [],
    }
    data["sessions"].append(session)
    save_sessions(data)
    return session


@serialized_mutation
def save_response_map(session_id: str, responses: dict[str, float], merge: bool = True) -> dict[str, Any]:
    data = load_sessions()
    session = find_session(data, session_id)
    if not session:
        raise ValueError(f"Unknown session: {session_id}")

    if session.get("status") == "completed":
        raise ValueError("Completed session responses are immutable; create a new session to rescore")
    instrument_path = Path(session["instrument_path"])
    instrument = load_json(instrument_path)
    stored_hash = session.get("instrument_sha256")
    current_hash = hashlib.sha256(instrument_path.read_bytes()).hexdigest()
    if stored_hash is not None and stored_hash != current_hash:
        raise ValueError("Stored instrument fingerprint no longer matches the scoring source")
    normalized = validate_response_map(instrument, responses)
    if merge:
        merged = dict(session.get("responses", {}))
        merged.update(normalized)
        session["responses"] = merged
    else:
        session["responses"] = normalized
    save_sessions(data)
    return session


def save_responses(session_id: str, responses_path: str, merge: bool = True) -> dict[str, Any]:
    responses = parse_responses(Path(responses_path))
    return save_response_map(session_id, responses, merge=merge)


@serialized_mutation
def score_session(session_id: str, completed_at: str) -> dict[str, Any]:
    data = load_sessions()
    session = find_session(data, session_id)
    if not session:
        raise ValueError(f"Unknown session: {session_id}")

    instrument_path = Path(session["instrument_path"])
    instrument = load_json(instrument_path)
    stored_hash = session.get("instrument_sha256")
    current_hash = hashlib.sha256(instrument_path.read_bytes()).hexdigest()
    if stored_hash is not None and stored_hash != current_hash:
        raise ValueError("Stored instrument fingerprint no longer matches the scoring source")
    responses = {str(key): float(value) for key, value in session.get("responses", {}).items()}
    validate_response_map(instrument, responses)
    if session.get("status") == "completed" and any(has_user_review(atom) for atom in session.get("profile_atoms", [])):
        raise ValueError("Reviewed profile atoms cannot be overwritten by rescoring; create a new session")
    completed_at = normalize_utc_timestamp(completed_at, "completed_at")
    output = generate_output(instrument, responses, session_id, completed_at)

    session["completed_at"] = completed_at
    session["status"] = "completed"
    session["scores"] = output["scores"]
    session["profile_atoms"] = output["profile_atoms"]
    save_sessions(data)
    return session


def show_session(session_id: str) -> dict[str, Any]:
    data = load_sessions()
    session = find_session(data, session_id)
    if not session:
        raise ValueError(f"Unknown session: {session_id}")
    return session


@serialized_mutation
def delete_session(session_id: str) -> dict[str, Any]:
    data = load_sessions()
    for index, session in enumerate(data["sessions"]):
        if session["session_id"] == session_id:
            removed = data["sessions"].pop(index)
            remaining_events = []
            removed_event_count = 0
            prefix = f"{session_id}::"
            for event in data.get("generation_feedback", []):
                refs = [ref for ref in event.get("atom_refs", []) if not ref.startswith(prefix)]
                if not refs:
                    removed_event_count += 1
                    continue
                event["atom_refs"] = refs
                remaining_events.append(event)
            if "generation_feedback" in data:
                data["generation_feedback"] = remaining_events
            save_sessions(data)
            return {**summarize_session(removed), "generation_feedback_events_deleted": removed_event_count}
    raise ValueError(f"Unknown session: {session_id}")


@serialized_mutation
def delete_session_responses(session_id: str, deleted_at: str) -> dict[str, Any]:
    data = load_sessions()
    session = find_session(data, session_id)
    if not session:
        raise ValueError(f"Unknown session: {session_id}")
    deleted_count = len(session.get("responses", {}))
    session["responses"] = {}
    session["responses_deleted_at"] = normalize_utc_timestamp(deleted_at, "deleted_at")
    save_sessions(data)
    return {"session_id": session_id, "deleted_response_count": deleted_count}


@serialized_mutation
def delete_session_profile_atoms(session_id: str, deleted_at: str) -> dict[str, Any]:
    data = load_sessions()
    session = find_session(data, session_id)
    if not session:
        raise ValueError(f"Unknown session: {session_id}")
    deleted_count = len(session.get("profile_atoms", []))
    session["profile_atoms"] = []
    session["profile_atoms_deleted_at"] = normalize_utc_timestamp(deleted_at, "deleted_at")
    prefix = f"{session_id}::"
    remaining_events = []
    removed_event_count = 0
    for event in data.get("generation_feedback", []):
        refs = [ref for ref in event.get("atom_refs", []) if not ref.startswith(prefix)]
        if not refs:
            removed_event_count += 1
            continue
        event["atom_refs"] = refs
        remaining_events.append(event)
    if "generation_feedback" in data:
        data["generation_feedback"] = remaining_events
    save_sessions(data)
    return {
        "session_id": session_id,
        "deleted_profile_atom_count": deleted_count,
        "generation_feedback_events_deleted": removed_event_count,
    }


def find_atom(session: dict[str, Any], atom_id: str) -> dict[str, Any] | None:
    for atom in session.get("profile_atoms", []):
        if atom["id"] == atom_id:
            return atom
    return None


@serialized_mutation
def review_atom(
    session_id: str,
    atom_id: str,
    reviewed_at: str,
    user_feedback: str | None = None,
    state: str | None = None,
    activation_scope: str | None = None,
    claim: str | None = None,
    user_note: str | None = None,
) -> dict[str, Any]:
    data = load_sessions()
    session = find_session(data, session_id)
    if not session:
        raise ValueError(f"Unknown session: {session_id}")

    atom = find_atom(session, atom_id)
    if not atom:
        raise ValueError(f"Unknown atom `{atom_id}` in session `{session_id}`")

    if user_feedback is not None and user_feedback not in USER_FEEDBACK_VALUES:
        raise ValueError(f"Invalid user feedback: {user_feedback}")
    if state is not None and state not in ATOM_STATE_VALUES:
        raise ValueError(f"Invalid atom state: {state}")
    if activation_scope is not None and activation_scope not in ACTIVATION_SCOPE_VALUES:
        raise ValueError(f"Invalid activation scope: {activation_scope}")
    if claim is not None:
        claim = claim.strip()
        if not claim:
            raise ValueError("Atom claim cannot be empty")
    if user_note is not None:
        user_note = user_note.strip()

    reviewed_at = normalize_utc_timestamp(reviewed_at, "reviewed_at")
    atom.setdefault("original_claim", atom.get("claim", ""))
    atom.setdefault("user_note", "")
    atom.setdefault("review_history", [])
    previous = {
        "claim": atom.get("claim"),
        "user_note": atom.get("user_note", ""),
        "user_feedback": atom.get("user_feedback"),
        "state": atom.get("state"),
        "activation_scope": atom.get("activation_scope"),
    }

    proposed = dict(atom)
    if user_feedback is not None:
        proposed["user_feedback"] = user_feedback
    if state is not None:
        proposed["state"] = state
    if activation_scope is not None:
        proposed["activation_scope"] = activation_scope
    if claim is not None:
        proposed["claim"] = claim
    if user_note is not None:
        proposed["user_note"] = user_note
    validate_atom_lifecycle(proposed)
    atom.update(proposed)

    current = {key: atom.get(key) for key in previous}
    changes = {
        key: {"from": previous[key], "to": current[key]}
        for key in previous
        if previous[key] != current[key]
    }
    if not changes:
        return atom
    atom["review_history"].append({"reviewed_at": reviewed_at, "changes": changes})
    atom["last_updated"] = reviewed_at

    save_sessions(data)
    return atom


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assessment session storage for Sol MVP.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Initialize the assessment sessions JSONDB.")

    subparsers.add_parser("list-sessions", help="List stored assessment response sessions.")

    subparsers.add_parser("list-profile-atoms", help="List derived profile atoms across stored sessions.")

    context_parser = subparsers.add_parser("export-profile-context", help="Build scoped profile context JSON.")
    context_parser.add_argument("--generated-at", required=True)
    context_parser.add_argument("--include-review-only", action="store_true")

    feedback_parser = subparsers.add_parser("record-generation-feedback", help="Store pilot feedback.")
    feedback_parser.add_argument("--event-id", required=True)
    feedback_parser.add_argument("--pilot-id", required=True)
    feedback_parser.add_argument("--recorded-at", required=True)
    feedback_parser.add_argument("--feedback", required=True, choices=sorted(GENERATION_FEEDBACK_VALUES))
    feedback_parser.add_argument("--atom-ref", required=True, action="append", dest="atom_refs")
    feedback_parser.add_argument("--note", default="")

    create_parser = subparsers.add_parser("create-session", help="Create a new assessment response session.")
    create_parser.add_argument("--session-id", required=True)
    create_parser.add_argument("--instrument", required=True, help="Path to instrument JSON.")
    create_parser.add_argument("--started-at", required=True)
    create_parser.add_argument("--consent-at", required=True)
    create_parser.add_argument("--user-id")

    save_parser = subparsers.add_parser("save-responses", help="Save raw responses to a session.")
    save_parser.add_argument("--session-id", required=True)
    save_parser.add_argument("--responses", required=True, help="Path to responses JSON.")
    save_parser.add_argument("--replace", action="store_true", help="Replace instead of merge responses.")

    score_parser = subparsers.add_parser("score-session", help="Score a completed session and derive profile atoms.")
    score_parser.add_argument("--session-id", required=True)
    score_parser.add_argument("--completed-at", required=True)

    show_parser = subparsers.add_parser("show-session", help="Show a stored session.")
    show_parser.add_argument("--session-id", required=True)

    delete_parser = subparsers.add_parser("delete-session", help="Delete a stored session.")
    delete_parser.add_argument("--session-id", required=True)

    delete_responses_parser = subparsers.add_parser("delete-session-responses", help="Delete raw responses only.")
    delete_responses_parser.add_argument("--session-id", required=True)
    delete_responses_parser.add_argument("--deleted-at", required=True)

    delete_atoms_parser = subparsers.add_parser("delete-session-profile-atoms", help="Delete derived atoms only.")
    delete_atoms_parser.add_argument("--session-id", required=True)
    delete_atoms_parser.add_argument("--deleted-at", required=True)

    review_parser = subparsers.add_parser("review-atom", help="Update user review state for a derived profile atom.")
    review_parser.add_argument("--session-id", required=True)
    review_parser.add_argument("--atom-id", required=True)
    review_parser.add_argument("--reviewed-at", required=True)
    review_parser.add_argument("--user-feedback", choices=["unconfirmed", "confirmed", "edited", "rejected"])
    review_parser.add_argument("--state", choices=["observed_candidate", "provisional_atom", "active_atom", "suppressed_atom"])
    review_parser.add_argument("--activation-scope", choices=["review_only", "contextual", "global"])
    review_parser.add_argument("--claim", help="Optional replacement claim text after review.")
    review_parser.add_argument("--user-note", help="Optional user-authored note; pass an empty value to clear it.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "init-db":
        ensure_db()
        print(json.dumps({"path": sessions_db_path().as_posix(), "status": "initialized"}, indent=2))
        return
    if args.command == "create-session":
        result = create_session(args.session_id, args.instrument, args.started_at, args.consent_at, args.user_id)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "list-sessions":
        result = list_sessions()
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "list-profile-atoms":
        result = list_profile_atoms()
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "export-profile-context":
        result = build_profile_context(args.generated_at, include_review_only=args.include_review_only)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "record-generation-feedback":
        result = record_generation_feedback(
            args.event_id,
            args.pilot_id,
            args.recorded_at,
            args.feedback,
            args.atom_refs,
            args.note,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "save-responses":
        result = save_responses(args.session_id, args.responses, merge=not args.replace)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "score-session":
        result = score_session(args.session_id, args.completed_at)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "show-session":
        result = show_session(args.session_id)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "delete-session":
        result = delete_session(args.session_id)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "delete-session-responses":
        result = delete_session_responses(args.session_id, args.deleted_at)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "delete-session-profile-atoms":
        result = delete_session_profile_atoms(args.session_id, args.deleted_at)
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == "review-atom":
        result = review_atom(
            args.session_id,
            args.atom_id,
            args.reviewed_at,
            user_feedback=args.user_feedback,
            state=args.state,
            activation_scope=args.activation_scope,
            claim=args.claim,
            user_note=args.user_note,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
