#!/usr/bin/env python3
"""Local JSONDB-backed assessment session store for the assessment-first MVP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from assessment_to_profile_atoms import generate_output, load_json, parse_responses


ROOT = Path(".")
JSONDB = ROOT / "jsondb"
SESSIONS_DB = JSONDB / "assessment_sessions.json"


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_db() -> None:
    JSONDB.mkdir(parents=True, exist_ok=True)
    if not SESSIONS_DB.exists():
        save_json(SESSIONS_DB, {"version": 1, "sessions": []})


def load_sessions() -> dict[str, Any]:
    ensure_db()
    return load_json(SESSIONS_DB)


def save_sessions(data: dict[str, Any]) -> None:
    save_json(SESSIONS_DB, data)


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


def create_session(
    session_id: str,
    instrument_path: str,
    started_at: str,
    user_id: str | None = None,
) -> dict[str, Any]:
    data = load_sessions()
    if find_session(data, session_id):
        raise ValueError(f"Session already exists: {session_id}")

    instrument = load_json(Path(instrument_path))
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "instrument_id": instrument["id"],
        "instrument_name": instrument["name"],
        "instrument_path": instrument_path,
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


def save_response_map(session_id: str, responses: dict[str, float], merge: bool = True) -> dict[str, Any]:
    data = load_sessions()
    session = find_session(data, session_id)
    if not session:
        raise ValueError(f"Unknown session: {session_id}")

    normalized = {str(key): float(value) for key, value in responses.items()}
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


def score_session(session_id: str, completed_at: str) -> dict[str, Any]:
    data = load_sessions()
    session = find_session(data, session_id)
    if not session:
        raise ValueError(f"Unknown session: {session_id}")

    instrument = load_json(Path(session["instrument_path"]))
    responses = {str(key): float(value) for key, value in session.get("responses", {}).items()}
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


def delete_session(session_id: str) -> dict[str, Any]:
    data = load_sessions()
    for index, session in enumerate(data["sessions"]):
        if session["session_id"] == session_id:
            removed = data["sessions"].pop(index)
            save_sessions(data)
            return summarize_session(removed)
    raise ValueError(f"Unknown session: {session_id}")


def find_atom(session: dict[str, Any], atom_id: str) -> dict[str, Any] | None:
    for atom in session.get("profile_atoms", []):
        if atom["id"] == atom_id:
            return atom
    return None


def review_atom(
    session_id: str,
    atom_id: str,
    reviewed_at: str,
    user_feedback: str | None = None,
    state: str | None = None,
    activation_scope: str | None = None,
    claim: str | None = None,
) -> dict[str, Any]:
    data = load_sessions()
    session = find_session(data, session_id)
    if not session:
        raise ValueError(f"Unknown session: {session_id}")

    atom = find_atom(session, atom_id)
    if not atom:
        raise ValueError(f"Unknown atom `{atom_id}` in session `{session_id}`")

    if user_feedback:
        atom["user_feedback"] = user_feedback
    if state:
        atom["state"] = state
    if activation_scope:
        atom["activation_scope"] = activation_scope
    if claim:
        atom["claim"] = claim
    atom["last_updated"] = reviewed_at

    save_sessions(data)
    return atom


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assessment session storage for Sol MVP.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Initialize the assessment sessions JSONDB.")

    subparsers.add_parser("list-sessions", help="List stored assessment response sessions.")

    subparsers.add_parser("list-profile-atoms", help="List derived profile atoms across stored sessions.")

    create_parser = subparsers.add_parser("create-session", help="Create a new assessment response session.")
    create_parser.add_argument("--session-id", required=True)
    create_parser.add_argument("--instrument", required=True, help="Path to instrument JSON.")
    create_parser.add_argument("--started-at", required=True)
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

    review_parser = subparsers.add_parser("review-atom", help="Update user review state for a derived profile atom.")
    review_parser.add_argument("--session-id", required=True)
    review_parser.add_argument("--atom-id", required=True)
    review_parser.add_argument("--reviewed-at", required=True)
    review_parser.add_argument("--user-feedback", choices=["unconfirmed", "confirmed", "edited", "rejected"])
    review_parser.add_argument("--state", choices=["observed_candidate", "provisional_atom", "active_atom", "suppressed_atom"])
    review_parser.add_argument("--activation-scope", choices=["review_only", "contextual", "global"])
    review_parser.add_argument("--claim", help="Optional replacement claim text after review.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "init-db":
        ensure_db()
        print(json.dumps({"path": SESSIONS_DB.as_posix(), "status": "initialized"}, indent=2))
        return
    if args.command == "create-session":
        result = create_session(args.session_id, args.instrument, args.started_at, args.user_id)
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
    if args.command == "review-atom":
        result = review_atom(
            args.session_id,
            args.atom_id,
            args.reviewed_at,
            user_feedback=args.user_feedback,
            state=args.state,
            activation_scope=args.activation_scope,
            claim=args.claim,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
