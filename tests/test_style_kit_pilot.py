import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if TOOLS.as_posix() not in sys.path:
    sys.path.insert(0, TOOLS.as_posix())

import style_kit_guidance as guidance
import style_kit_pilot as pilot
import style_kit_store as store
import validate_style_kit_contracts as contracts


BUNDLE_PATH = ROOT / "schemas" / "style_kit" / "v1" / "examples" / "valid-contract-bundle.json"


def load_valid_bundle() -> dict:
    return json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))


def proposed_guidance(bundle: dict, guidance_id: str = "guide_concise_v1") -> dict:
    record = copy.deepcopy(bundle["generation_guidance"][0])
    record["id"] = guidance_id
    record["user_state"] = "proposed"
    record["review_history"] = []
    record["provenance"]["guidance_version"] = 1
    record["updated_at"] = record["created_at"]
    return record


class SpyMockProvider(pilot.MockProvider):
    uri = "mock://spy-v1"

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate(self, request: dict) -> str:
        self.calls.append(copy.deepcopy(request))
        return super().generate(request)


class UnsafeMockProvider(pilot.MockProvider):
    uri = "mock://unsafe-v1"

    def generate(self, request: dict) -> str:
        return "Your personality is a diagnosis."


class ExternalProvider(pilot.MockProvider):
    uri = "https://provider.invalid/v1"
    mode = "external"


class StyleKitPilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db = os.environ.get(store.STYLE_KIT_DB_ENV)
        os.environ[store.STYLE_KIT_DB_ENV] = str(Path(self.tmp.name) / "style-kit-records.json")
        self.repository = store.JsonStyleKitRepository()
        self.bundle = load_valid_bundle()
        self.repository.create_record("sources", self.bundle["sources"][0])
        self.repository.create_record("observations", self.bundle["observations"][0])
        self.guidance_service = guidance.GuidanceService(self.repository)
        self.proposal = proposed_guidance(self.bundle)
        self.guidance_service.create_guidance(self.proposal)
        self.guidance_service.review_guidance(
            self.proposal["id"],
            "local_user",
            "2026-07-13T01:00:00Z",
            "confirmed",
        )
        self.pilot_service = pilot.PilotService(self.repository, self.guidance_service)

    def tearDown(self) -> None:
        if self.previous_db is None:
            os.environ.pop(store.STYLE_KIT_DB_ENV, None)
        else:
            os.environ[store.STYLE_KIT_DB_ENV] = self.previous_db
        self.tmp.cleanup()

    def create_run(
        self,
        run_id: str,
        *,
        provider_uri: str = pilot.DryRunProvider.uri,
        artifact_type: str = "project_description",
        guidance_ids: list[str] | None = None,
    ) -> dict:
        return self.pilot_service.create_run(
            run_id,
            "local_user",
            "2026-07-13T02:00:00-07:00",
            artifact_type,
            "Write a short project description.",
            "professional",
            guidance_ids if guidance_ids is not None else [self.proposal["id"]],
            provider_uri=provider_uri,
        )

    def test_dry_run_persists_exact_empty_variants_and_normalized_time(self) -> None:
        run = self.create_run("run_dry_v1")
        self.assertEqual(run["mode"], "dry_run")
        self.assertEqual(run["created_at"], "2026-07-13T09:00:00Z")
        self.assertEqual(run["completed_at"], "2026-07-13T09:00:00Z")
        self.assertEqual(run["status"], "completed")
        self.assertEqual({variant["kind"] for variant in run["variants"]}, {"generic", "personalized"})
        generic, personalized = run["variants"]
        self.assertEqual(generic["guidance_refs"], [])
        self.assertEqual(generic["guidance_snapshot"], [])
        self.assertEqual(generic["profile_atom_refs"], [])
        self.assertEqual(personalized["guidance_refs"], [self.proposal["id"]])
        self.assertEqual(personalized["guidance_snapshot"][0]["guidance_version"], 2)
        self.assertTrue(all(variant["output"] is None for variant in run["variants"]))
        self.assertTrue(all(variant["validation"]["status"] == "not_run" for variant in run["variants"]))
        self.assertEqual(run["task_sha256"], contracts.sha256_text(run["task_input"]))
        self.assertEqual(run["context_sha256"], contracts.context_sha256(run))
        self.assertTrue(all(variant["request_sha256"] == contracts.request_sha256(run, variant) for variant in run["variants"]))
        self.assertEqual(self.pilot_service.get_run(run["id"], "local_user"), run)

    def test_mock_runs_are_deterministic_and_generic_context_is_isolated(self) -> None:
        first = self.create_run("run_mock_one_v1", provider_uri=pilot.MockProvider.uri)
        second = self.create_run("run_mock_two_v1", provider_uri=pilot.MockProvider.uri)
        self.assertEqual(first["status"], "completed")
        self.assertEqual(second["status"], "completed")
        for first_variant, second_variant in zip(first["variants"], second["variants"], strict=True):
            self.assertEqual(first_variant["request_sha256"], second_variant["request_sha256"])
            self.assertEqual(first_variant["output"], second_variant["output"])
            self.assertEqual(first_variant["output_sha256"], second_variant["output_sha256"])
            self.assertEqual(first_variant["validation"], {"status": "passed", "validator_version": 1, "errors": []})
        generic, personalized = first["variants"]
        self.assertNotEqual(generic["output"], personalized["output"])
        self.assertEqual(generic["guidance_refs"], [])
        self.assertNotIn(self.proposal["prompt_safe_instruction"], generic["output"])

    def test_writing_guide_mock_enforces_required_sections(self) -> None:
        writing = proposed_guidance(self.bundle, "guide_writing_v1")
        writing["task_scopes"] = ["writing_guide"]
        self.guidance_service.create_guidance(writing)
        self.guidance_service.review_guidance(
            writing["id"],
            "local_user",
            "2026-07-13T01:01:00Z",
            "confirmed",
        )
        run = self.create_run(
            "run_guide_v1",
            provider_uri=pilot.MockProvider.uri,
            artifact_type="writing_guide",
            guidance_ids=[writing["id"]],
        )
        for variant in run["variants"]:
            self.assertEqual(pilot.validate_output("writing_guide", variant["output"]), [])
            self.assertIn("Useful defaults", variant["output"])
            self.assertIn("Questions to confirm", variant["output"])

    def test_ineligible_guidance_is_rejected_before_provider_call(self) -> None:
        spy = SpyMockProvider()
        service = pilot.PilotService(self.repository, self.guidance_service, [spy])
        self.guidance_service.disable_guidance(
            self.proposal["id"],
            "local_user",
            "2026-07-13T01:02:00Z",
        )
        with self.assertRaisesRegex(ValueError, "not eligible"):
            service.create_run(
                "run_blocked_v1",
                "local_user",
                "2026-07-13T02:00:00Z",
                "project_description",
                "Write a short project description.",
                "professional",
                [self.proposal["id"]],
                provider_uri=spy.uri,
            )
        self.assertEqual(spy.calls, [])
        self.assertIsNone(self.repository.get_record("pilot_runs", "run_blocked_v1"))

    def test_unsupported_external_and_invalid_requests_fail_without_runs(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported generation provider"):
            self.create_run("run_unknown_provider_v1", provider_uri="mock://missing")
        external = ExternalProvider()
        service = pilot.PilotService(self.repository, self.guidance_service, [external])
        with self.assertRaisesRegex(ValueError, "External generation provider mode is not approved"):
            service.create_run(
                "run_external_v1",
                "local_user",
                "2026-07-13T02:00:00Z",
                "project_description",
                "Write a short project description.",
                "professional",
                [self.proposal["id"]],
                provider_uri=external.uri,
            )
        with self.assertRaisesRegex(ValueError, "At least one reviewed guidance"):
            self.create_run("run_no_guidance_v1", guidance_ids=[])
        with self.assertRaisesRegex(ValueError, "run_id must match"):
            self.create_run("bad-run-id")
        with self.assertRaisesRegex(ValueError, "must include a timezone"):
            self.pilot_service.create_run(
                "run_bad_time_v1",
                "local_user",
                "2026-07-13T02:00:00",
                "project_description",
                "Write a short project description.",
                "professional",
                [self.proposal["id"]],
            )
        self.assertEqual(self.repository.list_records("pilot_runs"), [])

    def test_failed_output_validation_redacts_unsafe_provider_content(self) -> None:
        unsafe = UnsafeMockProvider()
        service = pilot.PilotService(self.repository, self.guidance_service, [unsafe])
        run = service.create_run(
            "run_unsafe_v1",
            "local_user",
            "2026-07-13T02:00:00Z",
            "project_description",
            "Write a short project description.",
            "professional",
            [self.proposal["id"]],
            provider_uri=unsafe.uri,
        )
        self.assertEqual(run["status"], "failed")
        self.assertTrue(all(variant["output"] is None for variant in run["variants"]))
        self.assertTrue(all(variant["output_sha256"] is None for variant in run["variants"]))
        self.assertTrue(all(variant["validation"]["status"] == "failed" for variant in run["variants"]))
        self.assertTrue(any("prohibited framing" in error for error in run["variants"][0]["validation"]["errors"]))
        self.assertNotIn("Your personality", self.repository.path.read_text(encoding="utf-8"))

    def test_output_validator_boundaries_are_explicit(self) -> None:
        self.assertIn("non-empty", pilot.validate_output("project_description", "")[0])
        self.assertTrue(any("35 to 300 words" in error for error in pilot.validate_output("project_description", "Too short.")))
        oversized = "word " * 301
        self.assertTrue(any("35 to 300 words" in error for error in pilot.validate_output("project_description", oversized)))
        identity_claim = "This text says your personality is fixed. " + ("context " * 35)
        self.assertTrue(any("prohibited framing" in error for error in pilot.validate_output("project_description", identity_claim)))
        self.assertTrue(any("missing section" in error for error in pilot.validate_output("writing_guide", "Useful defaults only")))

    def test_guidance_change_during_generation_prevents_stale_snapshot_write(self) -> None:
        guidance_service = self.guidance_service
        guidance_id = self.proposal["id"]

        class MutatingMockProvider(pilot.MockProvider):
            uri = "mock://mutating-v1"

            def __init__(self) -> None:
                self.changed = False

            def generate(self, request: dict) -> str:
                if not self.changed:
                    guidance_service.disable_guidance(
                        guidance_id,
                        "local_user",
                        "2026-07-13T01:03:00Z",
                    )
                    self.changed = True
                return super().generate(request)

        provider = MutatingMockProvider()
        service = pilot.PilotService(self.repository, self.guidance_service, [provider])
        with self.assertRaisesRegex(ValueError, "Guidance changed while creating pilot run"):
            service.create_run(
                "run_stale_v1",
                "local_user",
                "2026-07-13T02:00:00Z",
                "project_description",
                "Write a short project description.",
                "professional",
                [guidance_id],
                provider_uri=provider.uri,
            )
        self.assertIsNone(self.repository.get_record("pilot_runs", "run_stale_v1"))


if __name__ == "__main__":
    unittest.main()
