#!/usr/bin/env python3
"""Blinded evaluation lifecycle for persisted Creative Style Kit pilot runs."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from style_kit_store import StyleKitRepository
from time_contracts import normalize_utc_iso, normalized_utc_datetime


EVALUATION_CONTRACT_VERSION = 1
EVALUATION_LABELS = {"accurate", "useful", "too_strong", "too_generic", "wrong"}
NEGATIVE_LABELS = {"too_strong", "too_generic", "wrong"}
NON_VARIANT_SELECTIONS = {"tie", "cannot_judge"}


def validate_rating(value: int | None, field: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
        raise ValueError(f"{field} must be an integer from 1 through 5 or null")


class EvaluationService:
    """Create, inspect, export, and redact evaluations bound to exact runs."""

    def __init__(self, repository: StyleKitRepository) -> None:
        self.repository = repository

    def record_blinded_choice(
        self,
        event_id: str,
        owner_id: str,
        run_id: str,
        presented_variant_order: list[str],
        selection: str,
        choice_recorded_at: str,
    ) -> dict[str, Any]:
        if not isinstance(event_id, str) or re.fullmatch(r"eval_[a-z0-9][a-z0-9._-]{2,194}", event_id) is None:
            raise ValueError("event_id must match the Style Kit evaluation id contract")
        choice_at = normalize_utc_iso(choice_recorded_at, "choice_recorded_at")
        run = self.repository.get_record("pilot_runs", run_id)
        if run is None:
            raise ValueError(f"Unknown Style Kit pilot run: {run_id}")
        if run.get("owner_id") != owner_id:
            raise ValueError("Evaluation owner does not match pilot run owner")
        if run.get("record_state") != "active" or run.get("status") != "completed" or run.get("mode") != "mock":
            raise ValueError("Evaluation requires an active completed mock run")
        variants = run.get("variants", [])
        variant_by_id = {variant["variant_id"]: variant for variant in variants}
        if (
            len(presented_variant_order) != 2
            or len(set(presented_variant_order)) != 2
            or set(presented_variant_order) != set(variant_by_id)
        ):
            raise ValueError("presented_variant_order must contain each run variant exactly once")
        if any(
            variant.get("output") is None or variant.get("validation", {}).get("status") != "passed"
            for variant in variants
        ):
            raise ValueError("Evaluation requires two passed visible run outputs")

        if selection in NON_VARIANT_SELECTIONS:
            choice = selection
            selected_variant_id = None
        else:
            selected = variant_by_id.get(selection)
            if selected is None:
                raise ValueError("selection must be a presented variant id, tie, or cannot_judge")
            choice = selected["kind"]
            selected_variant_id = selection

        event = {
            "schema_version": "sol.style-kit.evaluation-event.v1",
            "id": event_id,
            "owner_id": owner_id,
            "consent_refs": deepcopy(run["consent_refs"]),
            "run_id": run_id,
            "evaluation_state": "choice_recorded",
            "was_blinded": True,
            "presented_variant_order": deepcopy(presented_variant_order),
            "selected_variant_id": selected_variant_id,
            "choice": choice,
            "feels_like_me": None,
            "usefulness": None,
            "labels": [],
            "correction": None,
            "affected_guidance_refs": [],
            "provenance": {
                "recorded_by": "user",
                "evaluation_contract_version": EVALUATION_CONTRACT_VERSION,
                "choice_recorded_at": choice_at,
                "identity_revealed_at": None,
                "revealed_after_choice": False,
            },
            "record_state": "active",
            "export_state": "exportable",
            "created_at": choice_at,
            "updated_at": choice_at,
            "deleted_at": None,
        }
        return self.repository.create_record("evaluation_events", event)

    def reveal_and_record_feedback(
        self,
        event_id: str,
        owner_id: str,
        identity_revealed_at: str,
        *,
        feels_like_me: int | None,
        usefulness: int | None,
        labels: list[str],
        correction: str | None = None,
        affected_guidance_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        reveal_at = normalize_utc_iso(identity_revealed_at, "identity_revealed_at")
        validate_rating(feels_like_me, "feels_like_me")
        validate_rating(usefulness, "usefulness")
        if len(labels) != len(set(labels)):
            raise ValueError("Evaluation labels must be unique")
        invalid_labels = sorted(set(labels) - EVALUATION_LABELS)
        if invalid_labels:
            raise ValueError(f"Unknown evaluation labels: {', '.join(invalid_labels)}")
        normalized_correction = correction.strip() if isinstance(correction, str) else None
        if set(labels) & NEGATIVE_LABELS and not normalized_correction:
            raise ValueError("Negative evaluation labels require a correction")
        if normalized_correction is not None and len(normalized_correction) > 2000:
            raise ValueError("correction must be 2000 characters or fewer")
        affected = affected_guidance_refs or []
        if len(affected) != len(set(affected)):
            raise ValueError("affected_guidance_refs must be unique")

        def mutation(existing: dict[str, Any]) -> dict[str, Any]:
            if existing.get("owner_id") != owner_id:
                raise ValueError("Evaluation owner does not match the requested owner")
            if existing.get("evaluation_state") != "choice_recorded":
                raise ValueError("Only a recorded blinded choice can be revealed")
            choice_at = existing["provenance"]["choice_recorded_at"]
            if normalized_utc_datetime(reveal_at) <= normalized_utc_datetime(choice_at):
                raise ValueError("identity_revealed_at must be later than choice_recorded_at")
            run = self.repository.get_record("pilot_runs", existing["run_id"])
            if run is None or run.get("owner_id") != owner_id:
                raise ValueError("Evaluation pilot run is missing or has the wrong owner")
            personalized = next(variant for variant in run["variants"] if variant["kind"] == "personalized")
            used_guidance = set(personalized["guidance_refs"])
            unknown_guidance = sorted(set(affected) - used_guidance)
            if unknown_guidance:
                raise ValueError(f"Evaluation references guidance not used by the run: {', '.join(unknown_guidance)}")
            candidate = deepcopy(existing)
            candidate.update(
                {
                    "evaluation_state": "revealed",
                    "feels_like_me": feels_like_me,
                    "usefulness": usefulness,
                    "labels": deepcopy(labels),
                    "correction": normalized_correction,
                    "affected_guidance_refs": deepcopy(affected),
                    "updated_at": reveal_at,
                }
            )
            candidate["provenance"]["identity_revealed_at"] = reveal_at
            candidate["provenance"]["revealed_after_choice"] = True
            return candidate

        return self.repository.mutate_record("evaluation_events", event_id, mutation)

    def get_evaluation(self, event_id: str, owner_id: str) -> dict[str, Any]:
        event = self.repository.get_record("evaluation_events", event_id)
        if event is None:
            raise KeyError(f"Unknown Style Kit evaluation event: {event_id}")
        if event.get("owner_id") != owner_id:
            raise ValueError("Evaluation owner does not match the requested owner")
        return event

    def list_evaluations(
        self,
        owner_id: str,
        *,
        include_deleted: bool = False,
    ) -> list[dict[str, Any]]:
        events = [
            event
            for event in self.repository.list_records("evaluation_events")
            if event.get("owner_id") == owner_id
            and (include_deleted or event.get("record_state") != "deleted")
        ]
        events.sort(key=lambda event: event.get("created_at") or "", reverse=True)
        return events

    def delete_evaluation(
        self,
        event_id: str,
        owner_id: str,
        deleted_at: str,
    ) -> dict[str, Any]:
        normalized_at = normalize_utc_iso(deleted_at, "deleted_at")

        def mutation(existing: dict[str, Any]) -> dict[str, Any]:
            if existing.get("owner_id") != owner_id:
                raise ValueError("Evaluation owner does not match the requested owner")
            if existing.get("record_state") == "deleted":
                raise ValueError("Evaluation event is already deleted")
            if normalized_utc_datetime(normalized_at) <= normalized_utc_datetime(existing["updated_at"]):
                raise ValueError("deleted_at must be later than the current evaluation update")
            candidate = deepcopy(existing)
            candidate.update(
                {
                    "consent_refs": [],
                    "presented_variant_order": [],
                    "selected_variant_id": None,
                    "choice": None,
                    "feels_like_me": None,
                    "usefulness": None,
                    "labels": [],
                    "correction": None,
                    "affected_guidance_refs": [],
                    "evaluation_state": "deleted",
                    "record_state": "deleted",
                    "export_state": "deleted",
                    "updated_at": normalized_at,
                    "deleted_at": normalized_at,
                }
            )
            candidate["provenance"]["choice_recorded_at"] = None
            candidate["provenance"]["identity_revealed_at"] = None
            candidate["provenance"]["revealed_after_choice"] = False
            return candidate

        return self.repository.mutate_record("evaluation_events", event_id, mutation)
