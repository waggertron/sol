#!/usr/bin/env python3
"""Run the local assessment-first MVP flow end to end."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from assessment_session_store import create_session, save_responses, score_session


ROOT = Path(".")
ARTIFACTS_DIR = ROOT / "artifacts" / "assessment_runs"


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_summary(session: dict[str, Any]) -> dict[str, Any]:
    summary_atoms = []
    for atom in session.get("profile_atoms", []):
        metadata = atom.get("assessment_metadata", {})
        summary_atoms.append(
            {
                "id": atom["id"],
                "label": atom["label"],
                "claim": atom["claim"],
                "state": atom["state"],
                "activation_scope": atom["activation_scope"],
                "confidence": atom["confidence"],
                "trait": metadata.get("trait"),
                "normalized_score": metadata.get("normalized_score"),
                "score_value": metadata.get("score_value"),
                "score_range": metadata.get("score_range"),
            }
        )

    return {
        "session_id": session["session_id"],
        "instrument_id": session["instrument_id"],
        "instrument_name": session["instrument_name"],
        "status": session["status"],
        "started_at": session["started_at"],
        "completed_at": session["completed_at"],
        "response_count": len(session.get("responses", {})),
        "score_count": len(session.get("scores", [])),
        "profile_atom_count": len(session.get("profile_atoms", [])),
        "profile_atoms": summary_atoms,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local assessment-first MVP flow.")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--instrument", required=True, help="Path to instrument JSON.")
    parser.add_argument("--responses", required=True, help="Path to responses JSON.")
    parser.add_argument("--started-at", required=True)
    parser.add_argument("--consent-at", help="Consent timestamp; defaults to --started-at for local fixtures.")
    parser.add_argument("--completed-at", required=True)
    parser.add_argument("--user-id")
    parser.add_argument(
        "--artifact-dir",
        default=ARTIFACTS_DIR,
        type=Path,
        help="Directory where full and summary artifacts will be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    create_session(args.session_id, args.instrument, args.started_at, args.consent_at or args.started_at, args.user_id)
    save_responses(args.session_id, args.responses, merge=True)
    session = score_session(args.session_id, args.completed_at)

    artifact_dir = args.artifact_dir / args.session_id
    full_path = artifact_dir / "session.json"
    summary_path = artifact_dir / "summary.json"
    save_json(full_path, session)
    save_json(summary_path, build_summary(session))

    print(
        json.dumps(
            {
                "session_id": args.session_id,
                "full_artifact": full_path.as_posix(),
                "summary_artifact": summary_path.as_posix(),
                "profile_atom_count": len(session.get("profile_atoms", [])),
                "score_count": len(session.get("scores", [])),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
