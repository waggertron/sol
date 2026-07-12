#!/usr/bin/env python3
"""Persisted dry-run and deterministic mock pilots for the Creative Style Kit."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import re
from typing import Any, Protocol

from style_kit_guidance import GuidanceService
from style_kit_store import StyleKitRepository
from time_contracts import normalize_utc_iso
from validate_style_kit_contracts import context_sha256, request_sha256, sha256_text


PROMPT_CONTRACT_VERSION = 1
OUTPUT_VALIDATOR_VERSION = 1
APPLICATION_VERSION = "style-kit-pilot-v1"
SUPPORTED_ARTIFACTS = {"writing_guide", "project_description"}
SUPPORTED_CONTEXTS = {"general", "professional", "public", "reflective", "creative"}
PROHIBITED_OUTPUT_PHRASES = {
    "diagnosis",
    "intelligence score",
    "mental illness",
    "mind reader",
    "protected class",
    "true personality",
    "you are inherently",
    "your personality is",
    '"role": "system"',
    "<system>",
}


class GenerationProvider(Protocol):
    uri: str
    mode: str
    provider_version: str
    model: str | None

    def generate(self, request: dict[str, Any]) -> str | None: ...


class DryRunProvider:
    uri = "dry-run://style-kit-v1"
    mode = "dry_run"
    provider_version = "1"
    model = None

    def generate(self, request: dict[str, Any]) -> None:
        return None


class MockProvider:
    uri = "mock://style-kit-v1"
    mode = "mock"
    provider_version = "1"
    model = None

    def generate(self, request: dict[str, Any]) -> str:
        artifact_type = request["artifact_type"]
        seed = int(request["request_sha256"][:8], 16)
        if artifact_type == "writing_guide":
            defaults = [
                "Lead with the purpose, then give one concrete example.",
                "Use a clear opening, practical detail, and an explicit next step.",
                "Prefer compact sections that make the action easy to find.",
            ]
            adjustments = [
                "Add detail when the task is reflective or the audience needs context.",
                "Use more explanation when precision matters more than speed.",
                "Adjust warmth and detail to the stated audience and setting.",
            ]
            evidence_note = (
                "- Apply only the reviewed preferences recorded for this task."
                if request["variant_kind"] == "personalized"
                else "- Treat these as general drafting defaults, not user-specific evidence."
            )
            return (
                "Useful defaults\n"
                f"- {defaults[seed % len(defaults)]}\n\n"
                "Context-specific adjustments\n"
                f"- {adjustments[(seed // 3) % len(adjustments)]}\n\n"
                "Things to avoid assuming\n"
                f"{evidence_note}\n\n"
                "Questions to confirm\n"
                "- Should this task prioritize brevity, detail, warmth, or formality?"
            )
        if artifact_type == "project_description":
            openings = [
                "This project turns a complex workflow into a clear, inspectable local experience.",
                "This project provides a focused local workflow for organizing complex work.",
                "This project makes a complicated process easier to review, correct, and repeat.",
            ]
            closings = [
                "The result is a practical foundation that can be tested before broader expansion.",
                "Each step stays visible, correctable, and grounded in the evidence used.",
                "The initial scope stays narrow so usefulness and safety can be evaluated directly.",
            ]
            if request["variant_kind"] == "personalized":
                middle = (
                    "It applies only the reviewed, task-scoped guidance selected for this run while "
                    "keeping sources, decisions, and outputs connected. The first version emphasizes "
                    "explicit user control, reproducible behavior, and comparison with a generic baseline."
                )
            else:
                middle = (
                    "It uses general drafting defaults while keeping sources, decisions, and outputs "
                    "connected without presenting tentative evidence as certainty. The first version "
                    "emphasizes reproducible behavior and a small result that can be evaluated directly."
                )
            return f"{openings[seed % len(openings)]} {middle} {closings[(seed // 3) % len(closings)]}"
        raise ValueError(f"Mock provider does not support artifact type: {artifact_type}")


def validate_output(artifact_type: str, output: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(output, str) or not output.strip():
        return ["output must be a non-empty string"]
    if len(output) > 5000:
        errors.append("output exceeds 5000 characters")
    lowered = output.lower()
    for phrase in sorted(PROHIBITED_OUTPUT_PHRASES):
        if phrase in lowered:
            errors.append(f"output contains prohibited framing: {phrase}")
    words = output.split()
    if artifact_type == "project_description" and not 35 <= len(words) <= 300:
        errors.append("project_description output must contain 35 to 300 words")
    if artifact_type == "writing_guide":
        required_sections = (
            "Useful defaults",
            "Context-specific adjustments",
            "Things to avoid assuming",
            "Questions to confirm",
        )
        for section in required_sections:
            if section not in output:
                errors.append(f"writing_guide output is missing section: {section}")
    if artifact_type not in SUPPORTED_ARTIFACTS:
        errors.append(f"unsupported artifact type: {artifact_type}")
    return errors


def ordered_unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def guidance_snapshot(guidance: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": guidance["id"],
        "guidance_version": guidance["provenance"]["guidance_version"],
        "prompt_safe_instruction": guidance["prompt_safe_instruction"],
        "contexts": deepcopy(guidance["contexts"]),
        "task_scopes": deepcopy(guidance["task_scopes"]),
        "contraindications": deepcopy(guidance["contraindications"]),
        "observation_refs": deepcopy(guidance["observation_refs"]),
        "profile_atom_refs": deepcopy(guidance["profile_atom_refs"]),
    }


class PilotService:
    """Create persisted generic/personalized runs through local providers."""

    def __init__(
        self,
        repository: StyleKitRepository,
        guidance_service: GuidanceService,
        providers: list[GenerationProvider] | None = None,
    ) -> None:
        self.repository = repository
        self.guidance_service = guidance_service
        provider_list = providers if providers is not None else [DryRunProvider(), MockProvider()]
        self.providers = {provider.uri: provider for provider in provider_list}
        if len(self.providers) != len(provider_list):
            raise ValueError("Generation provider URIs must be unique")

    def _provider(self, provider_uri: str) -> GenerationProvider:
        provider = self.providers.get(provider_uri)
        if provider is None:
            raise ValueError(f"Unsupported generation provider: {provider_uri}")
        if provider.mode not in {"dry_run", "mock"}:
            raise ValueError(f"External generation provider mode is not approved: {provider.mode}")
        expected_prefix = "dry-run://" if provider.mode == "dry_run" else "mock://"
        if not provider.uri.startswith(expected_prefix):
            raise ValueError(f"Provider URI does not match mode {provider.mode}: {provider.uri}")
        return provider

    def create_run(
        self,
        run_id: str,
        owner_id: str,
        created_at: str,
        artifact_type: str,
        task_input: str,
        context: str,
        guidance_ids: list[str],
        *,
        provider_uri: str = DryRunProvider.uri,
    ) -> dict[str, Any]:
        normalized_at = normalize_utc_iso(created_at, "created_at")
        if not isinstance(run_id, str) or re.fullmatch(r"run_[a-z0-9][a-z0-9._-]{2,195}", run_id) is None:
            raise ValueError("run_id must match the Style Kit pilot-run id contract")
        if artifact_type not in SUPPORTED_ARTIFACTS:
            raise ValueError(f"Unsupported pilot artifact type: {artifact_type}")
        if context not in SUPPORTED_CONTEXTS:
            raise ValueError(f"Unsupported pilot context: {context}")
        if not isinstance(task_input, str) or not task_input.strip():
            raise ValueError("task_input is required")
        if len(task_input) > 10000:
            raise ValueError("task_input must be 10000 characters or fewer")
        if not guidance_ids:
            raise ValueError("At least one reviewed guidance id is required")
        if len(guidance_ids) != len(set(guidance_ids)):
            raise ValueError("Guidance ids must be unique")

        provider = self._provider(provider_uri)
        eligible = {
            item["id"]: item
            for item in self.guidance_service.eligible_guidance(
                owner_id,
                context=context,
                task_scope=artifact_type,
            )
        }
        ineligible = [guidance_id for guidance_id in guidance_ids if guidance_id not in eligible]
        if ineligible:
            raise ValueError(f"Guidance is missing or not eligible for this run: {', '.join(ineligible)}")
        selected = [eligible[guidance_id] for guidance_id in guidance_ids]
        snapshots = [guidance_snapshot(item) for item in selected]
        source_refs = ordered_unique([ref for item in selected for ref in item["source_refs"]])
        consent_refs = ordered_unique([ref for item in selected for ref in item["consent_refs"]])
        profile_atom_refs = ordered_unique([ref for item in selected for ref in item["profile_atom_refs"]])

        variant_suffix = hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:24]
        run: dict[str, Any] = {
            "schema_version": "sol.style-kit.pilot-run.v1",
            "id": run_id,
            "owner_id": owner_id,
            "consent_refs": consent_refs,
            "source_refs": source_refs,
            "mode": provider.mode,
            "provider": {
                "uri": provider.uri,
                "provider_version": provider.provider_version,
                "model": provider.model,
            },
            "external_provider_consent": False,
            "prompt_contract_version": PROMPT_CONTRACT_VERSION,
            "task_sha256": sha256_text(task_input),
            "context_sha256": "0" * 64,
            "artifact_type": artifact_type,
            "context": context,
            "task_input": task_input,
            "variants": [
                {
                    "variant_id": f"variant_{variant_suffix}_generic",
                    "kind": "generic",
                    "request_sha256": "0" * 64,
                    "guidance_refs": [],
                    "guidance_snapshot": [],
                    "profile_atom_refs": [],
                    "output": None,
                    "output_sha256": None,
                    "validation": {
                        "status": "not_run",
                        "validator_version": OUTPUT_VALIDATOR_VERSION,
                        "errors": [],
                    },
                },
                {
                    "variant_id": f"variant_{variant_suffix}_personalized",
                    "kind": "personalized",
                    "request_sha256": "0" * 64,
                    "guidance_refs": guidance_ids,
                    "guidance_snapshot": snapshots,
                    "profile_atom_refs": profile_atom_refs,
                    "output": None,
                    "output_sha256": None,
                    "validation": {
                        "status": "not_run",
                        "validator_version": OUTPUT_VALIDATOR_VERSION,
                        "errors": [],
                    },
                },
            ],
            "status": "completed",
            "provenance": {
                "created_by": "user",
                "application_version": APPLICATION_VERSION,
            },
            "record_state": "active",
            "export_state": "exportable",
            "created_at": normalized_at,
            "updated_at": normalized_at,
            "completed_at": normalized_at,
            "deleted_at": None,
        }
        run["context_sha256"] = context_sha256(run)
        for variant in run["variants"]:
            variant["request_sha256"] = request_sha256(run, variant)
            request = {
                "artifact_type": artifact_type,
                "task_input": task_input,
                "variant_kind": variant["kind"],
                "request_sha256": variant["request_sha256"],
                "guidance_snapshot": deepcopy(variant["guidance_snapshot"]),
            }
            output = provider.generate(request)
            if provider.mode == "dry_run":
                continue
            errors = validate_output(artifact_type, output)
            if errors:
                variant["validation"] = {
                    "status": "failed",
                    "validator_version": OUTPUT_VALIDATOR_VERSION,
                    "errors": errors,
                }
                run["status"] = "failed"
                continue
            variant["output"] = output
            variant["output_sha256"] = sha256_text(output)
            variant["validation"] = {
                "status": "passed",
                "validator_version": OUTPUT_VALIDATOR_VERSION,
                "errors": [],
            }
        expected_snapshots = {snapshot["id"]: snapshot for snapshot in snapshots}

        def persist(candidate_bundle: dict[str, Any]) -> dict[str, Any]:
            if any(existing.get("id") == run_id for existing in candidate_bundle["pilot_runs"]):
                raise ValueError(f"Duplicate Style Kit pilot run id: {run_id}")
            current_guidance = {item["id"]: item for item in candidate_bundle["generation_guidance"]}
            for guidance_id, expected_snapshot in expected_snapshots.items():
                current = current_guidance.get(guidance_id)
                if current is None or guidance_snapshot(current) != expected_snapshot:
                    raise ValueError(f"Guidance changed while creating pilot run: {guidance_id}")
                if not self.guidance_service.is_guidance_eligible(
                    current,
                    owner_id,
                    context=context,
                    task_scope=artifact_type,
                ):
                    raise ValueError(f"Guidance became ineligible while creating pilot run: {guidance_id}")
            candidate_bundle["pilot_runs"].append(deepcopy(run))
            return candidate_bundle

        persisted = self.repository.mutate_bundle(persist)
        return next(item for item in persisted["pilot_runs"] if item["id"] == run_id)

    def get_run(self, run_id: str, owner_id: str) -> dict[str, Any]:
        run = self.repository.get_record("pilot_runs", run_id)
        if run is None:
            raise KeyError(f"Unknown Style Kit pilot run: {run_id}")
        if run.get("owner_id") != owner_id:
            raise ValueError("Pilot run owner does not match the requested owner")
        return run
