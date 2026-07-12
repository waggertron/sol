"""Shared downstream eligibility policy for user-reviewed profile atoms."""

from __future__ import annotations

from typing import Any


def is_generation_eligible(atom: dict[str, Any] | None) -> bool:
    return bool(
        atom
        and atom.get("state") == "active_atom"
        and atom.get("activation_scope") in {"contextual", "global"}
        and atom.get("user_feedback") in {"confirmed", "edited"}
        and atom.get("sensitivity_level") != "blocked"
    )
