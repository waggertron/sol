#!/usr/bin/env python3
"""Render the first local, model-free generation pilot dry run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from assessment_session_store import build_profile_context


ROOT = Path(".")
DEFAULT_OUTPUT_ROOT = ROOT / "tmp" / "generation-pilot"


def generation_atoms(packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [atom for atom in packet.get("atoms", []) if atom.get("eligible_for_generation") is True]


def build_dry_run(generated_at: str) -> dict[str, Any]:
    packet = build_profile_context(generated_at)
    atoms = generation_atoms(packet)
    if not atoms:
        raise ValueError("No generation-eligible profile atoms are available; confirm an atom first")

    prompt_context = [
        {
            "id": atom["id"],
            "session_id": atom["session_id"],
            "claim": atom["claim"],
            "context": atom["context"],
            "confidence": atom["confidence"],
            "generation_guidance": atom["generation_guidance"],
            "contraindications": atom["contraindications"],
            "uncertainty": atom["uncertainty"],
        }
        for atom in atoms
    ]
    prompt = """Create a concise writing and communication style guide from the supplied user-reviewed profile context.

Requirements:
- Describe preferences as tentative, user-correctable guidance, not identity facts.
- Do not diagnose, infer protected traits, or make claims about intelligence, morality, competence, or mental health.
- Respect each atom's context and contraindications; do not generalize contextual evidence globally.
- Preserve uncertainty and mention when evidence comes from self-report assessment.
- Provide four sections: Useful defaults, Context-specific adjustments, Things to avoid assuming, and Questions to confirm.
- If an atom lacks concrete generation guidance, turn it into a confirmation question instead of inventing a style rule.
"""
    return {
        "pilot_version": 1,
        "mode": "dry_run",
        "artifact_type": "writing_communication_style_guide",
        "generated_at": generated_at,
        "external_model_called": False,
        "prompt": prompt,
        "profile_context": prompt_context,
        "safety": packet["safety"],
    }


def validate_output_path(path: Path) -> None:
    root = DEFAULT_OUTPUT_ROOT.resolve()
    resolved = path.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Output path must stay under {DEFAULT_OUTPUT_ROOT.as_posix()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the Sol writing-guide generation pilot dry run.")
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--output", type=Path, help="Optional JSON output under tmp/generation-pilot/.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_dry_run(args.generated_at)
    if args.output:
        validate_output_path(args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
