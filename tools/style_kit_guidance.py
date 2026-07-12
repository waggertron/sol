#!/usr/bin/env python3
"""User-reviewed generation-guidance lifecycle for the Creative Style Kit."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Callable

from profile_atom_policy import is_generation_eligible as profile_atom_is_eligible
from style_kit_store import StyleKitRepository


ProfileAtomLookup = Callable[[str], dict[str, Any] | None]
GUIDANCE_COLLECTION = "generation_guidance"
TRANSITIONS = {
    "proposed": {"confirmed", "edited", "disabled"},
    "confirmed": {"edited", "disabled"},
    "edited": {"edited", "disabled"},
    "disabled": set(),
}
EDITABLE_FIELDS = (
    "instruction",
    "prompt_safe_instruction",
    "contexts",
    "task_scopes",
    "contraindications",
)


def normalize_utc_timestamp(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("reviewed_at is required")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("reviewed_at must be an ISO-8601 timestamp with timezone") from exc
    if parsed.tzinfo is None:
        raise ValueError("reviewed_at must include a timezone")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class GuidanceService:
    """Guidance operations that require explicit user review before activation."""

    def __init__(
        self,
        repository: StyleKitRepository,
        profile_atom_lookup: ProfileAtomLookup | None = None,
    ) -> None:
        self.repository = repository
        self.profile_atom_lookup = profile_atom_lookup

    def _evidence_errors(self, guidance: dict[str, Any], activation: bool) -> list[str]:
        errors: list[str] = []
        observation_refs = guidance.get("observation_refs", [])
        profile_atom_refs = guidance.get("profile_atom_refs", [])
        if not observation_refs and not profile_atom_refs:
            errors.append("Guidance must reference an observation or eligible profile atom")

        for observation_ref in observation_refs:
            observation = self.repository.get_record("observations", observation_ref)
            if observation is None:
                errors.append(f"Unknown guidance observation: {observation_ref}")
                continue
            if observation.get("owner_id") != guidance.get("owner_id"):
                errors.append(f"Guidance owner does not match observation: {observation_ref}")
            if observation.get("record_state") != "active":
                errors.append(f"Guidance observation is not active: {observation_ref}")
            if observation.get("review_state") in {"rejected", "invalidated"}:
                errors.append(f"Guidance observation is not usable: {observation_ref}")
            if observation.get("sensitivity_level") not in {"low", "medium"}:
                errors.append(f"Guidance observation sensitivity is not eligible: {observation_ref}")
            if activation and observation.get("review_state") != "confirmed":
                errors.append(f"Guidance observation is not user-confirmed: {observation_ref}")

        for atom_ref in profile_atom_refs:
            atom = self.profile_atom_lookup(atom_ref) if self.profile_atom_lookup else None
            if not atom or atom.get("id") != atom_ref or not profile_atom_is_eligible(atom):
                errors.append(f"Profile atom is not generation-eligible: {atom_ref}")
        return errors

    def _require_evidence(self, guidance: dict[str, Any], activation: bool) -> None:
        errors = self._evidence_errors(guidance, activation)
        if errors:
            raise ValueError("; ".join(errors))

    def create_guidance(self, guidance: dict[str, Any]) -> dict[str, Any]:
        candidate = deepcopy(guidance)
        if candidate.get("user_state") != "proposed":
            raise ValueError("New guidance must start proposed and require user review")
        if candidate.get("record_state") != "active" or candidate.get("export_state") != "exportable":
            raise ValueError("New guidance must start active and exportable")
        if candidate.get("deleted_at") is not None:
            raise ValueError("New guidance cannot start deleted")
        if candidate.get("review_history"):
            raise ValueError("New proposed guidance cannot start with review history")
        if candidate.get("original_instruction") != candidate.get("instruction"):
            raise ValueError("New guidance instruction must match immutable original_instruction")
        self._require_evidence(candidate, activation=False)
        return self.repository.create_record(GUIDANCE_COLLECTION, candidate)

    def review_guidance(
        self,
        guidance_id: str,
        owner_id: str,
        reviewed_at: str,
        target_state: str,
        *,
        instruction: str | None = None,
        prompt_safe_instruction: str | None = None,
        contexts: list[str] | None = None,
        task_scopes: list[str] | None = None,
        contraindications: list[str] | None = None,
    ) -> dict[str, Any]:
        normalized_at = normalize_utc_timestamp(reviewed_at)
        requested_values = {
            "instruction": instruction,
            "prompt_safe_instruction": prompt_safe_instruction,
            "contexts": contexts,
            "task_scopes": task_scopes,
            "contraindications": contraindications,
        }

        def mutation(existing: dict[str, Any]) -> dict[str, Any]:
            if existing.get("owner_id") != owner_id:
                raise ValueError("Guidance owner does not match the requested owner")
            current_state = existing.get("user_state")
            if target_state not in TRANSITIONS.get(current_state, set()):
                raise ValueError(f"Invalid guidance transition: {current_state} -> {target_state}")
            if normalized_at <= normalize_utc_timestamp(existing.get("updated_at")):
                raise ValueError("reviewed_at must be later than the current guidance update")
            supplied_fields = [field for field, value in requested_values.items() if value is not None]
            if target_state == "confirmed" and supplied_fields:
                raise ValueError("Confirmed guidance cannot include edits; use the edited state")
            if target_state == "disabled" and supplied_fields:
                raise ValueError("Disable guidance separately from content edits")
            if instruction is not None and prompt_safe_instruction is None:
                raise ValueError("Instruction edits require a separate prompt_safe_instruction")

            candidate = deepcopy(existing)
            changes: list[dict[str, Any]] = []
            for field in EDITABLE_FIELDS:
                value = requested_values[field]
                if value is not None and value != candidate.get(field):
                    changes.append({"field": field, "from": deepcopy(candidate.get(field)), "to": deepcopy(value)})
                    candidate[field] = deepcopy(value)
            if target_state == "edited" and not changes:
                raise ValueError("Edited guidance requires at least one material guidance edit")
            changes.append({"field": "user_state", "from": current_state, "to": target_state})
            candidate["user_state"] = target_state
            candidate["updated_at"] = normalized_at
            candidate["provenance"]["guidance_version"] += 1
            candidate["review_history"].append(
                {
                    "reviewed_at": normalized_at,
                    "reviewed_by": "user",
                    "changes": changes,
                }
            )
            if target_state in {"confirmed", "edited"}:
                self._require_evidence(candidate, activation=True)
            return candidate

        return self.repository.mutate_record(GUIDANCE_COLLECTION, guidance_id, mutation)

    def disable_guidance(
        self,
        guidance_id: str,
        owner_id: str,
        reviewed_at: str,
    ) -> dict[str, Any]:
        return self.review_guidance(
            guidance_id,
            owner_id,
            reviewed_at,
            "disabled",
        )

    def eligible_guidance(
        self,
        owner_id: str,
        *,
        context: str | None = None,
        task_scope: str | None = None,
    ) -> list[dict[str, Any]]:
        eligible: list[dict[str, Any]] = []
        for guidance in self.repository.list_records(GUIDANCE_COLLECTION):
            if guidance.get("owner_id") != owner_id:
                continue
            if guidance.get("record_state") != "active":
                continue
            if guidance.get("user_state") not in {"confirmed", "edited"}:
                continue
            if context is not None and context not in guidance.get("contexts", []):
                continue
            if task_scope is not None and task_scope not in guidance.get("task_scopes", []):
                continue
            if not self._evidence_errors(guidance, activation=True):
                eligible.append(guidance)
        return eligible
