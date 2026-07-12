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

import style_kit_evaluation as evaluation
import style_kit_guidance as guidance
import style_kit_pilot as pilot
import style_kit_store as store


BUNDLE_PATH = ROOT / "schemas" / "style_kit" / "v1" / "examples" / "valid-contract-bundle.json"
ASSESSMENT_DB = ROOT / "jsondb" / "assessment_sessions.json"


def load_valid_bundle() -> dict:
    return json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))


def proposed_guidance(bundle: dict) -> dict:
    record = copy.deepcopy(bundle["generation_guidance"][0])
    record["user_state"] = "proposed"
    record["review_history"] = []
    record["provenance"]["guidance_version"] = 1
    record["updated_at"] = record["created_at"]
    return record


class StyleKitEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db = os.environ.get(store.STYLE_KIT_DB_ENV)
        os.environ[store.STYLE_KIT_DB_ENV] = str(Path(self.tmp.name) / "style-kit-records.json")
        self.repository = store.JsonStyleKitRepository()
        self.bundle = load_valid_bundle()
        self.repository.create_record("sources", self.bundle["sources"][0])
        self.repository.create_record("observations", self.bundle["observations"][0])
        self.guidance_service = guidance.GuidanceService(self.repository)
        self.guidance = proposed_guidance(self.bundle)
        self.guidance_service.create_guidance(self.guidance)
        self.guidance_service.review_guidance(
            self.guidance["id"],
            "local_user",
            "2026-07-13T01:00:00Z",
            "confirmed",
        )
        self.pilot_service = pilot.PilotService(self.repository, self.guidance_service)
        self.run = self.pilot_service.create_run(
            "run_evaluation_v1",
            "local_user",
            "2026-07-13T02:00:00Z",
            "project_description",
            "Write a short project description.",
            "professional",
            [self.guidance["id"]],
            provider_uri=pilot.MockProvider.uri,
        )
        self.service = evaluation.EvaluationService(self.repository)
        self.generic = next(variant for variant in self.run["variants"] if variant["kind"] == "generic")
        self.personalized = next(variant for variant in self.run["variants"] if variant["kind"] == "personalized")
        self.presented_order = [self.personalized["variant_id"], self.generic["variant_id"]]

    def tearDown(self) -> None:
        if self.previous_db is None:
            os.environ.pop(store.STYLE_KIT_DB_ENV, None)
        else:
            os.environ[store.STYLE_KIT_DB_ENV] = self.previous_db
        self.tmp.cleanup()

    def create_evaluation(
        self,
        event_id: str = "eval_choice_v1",
        *,
        selection: str | None = None,
        labels: list[str] | None = None,
        correction: str | None = None,
        affected_guidance_refs: list[str] | None = None,
    ) -> dict:
        self.service.record_blinded_choice(
            event_id,
            "local_user",
            self.run["id"],
            self.presented_order,
            selection or self.personalized["variant_id"],
            "2026-07-12T19:00:00-07:00",
        )
        return self.service.reveal_and_record_feedback(
            event_id,
            "local_user",
            "2026-07-13T02:00:01Z",
            feels_like_me=4,
            usefulness=5,
            labels=labels if labels is not None else ["accurate", "useful"],
            correction=correction,
            affected_guidance_refs=(
                affected_guidance_refs
                if affected_guidance_refs is not None
                else [self.guidance["id"]]
            ),
        )

    def test_blinded_selection_maps_to_variant_kind_after_reveal(self) -> None:
        choice = self.service.record_blinded_choice(
            "eval_choice_v1",
            "local_user",
            self.run["id"],
            self.presented_order,
            self.personalized["variant_id"],
            "2026-07-12T19:00:00-07:00",
        )
        self.assertEqual(choice["evaluation_state"], "choice_recorded")
        self.assertTrue(choice["was_blinded"])
        self.assertEqual(choice["presented_variant_order"], self.presented_order)
        self.assertEqual(choice["selected_variant_id"], self.personalized["variant_id"])
        self.assertEqual(choice["choice"], "personalized")
        self.assertIsNone(choice["provenance"]["identity_revealed_at"])
        self.assertFalse(choice["provenance"]["revealed_after_choice"])
        self.assertIsNone(choice["feels_like_me"])

        event = self.service.reveal_and_record_feedback(
            choice["id"],
            "local_user",
            "2026-07-13T02:00:01Z",
            feels_like_me=4,
            usefulness=5,
            labels=["accurate", "useful"],
            affected_guidance_refs=[self.guidance["id"]],
        )
        self.assertEqual(event["evaluation_state"], "revealed")
        self.assertEqual(event["consent_refs"], self.run["consent_refs"])
        self.assertEqual(event["affected_guidance_refs"], [self.guidance["id"]])
        self.assertEqual(event["provenance"]["choice_recorded_at"], "2026-07-13T02:00:00Z")
        self.assertEqual(event["provenance"]["identity_revealed_at"], "2026-07-13T02:00:01Z")
        self.assertEqual(event["created_at"], "2026-07-13T02:00:00Z")
        self.assertEqual(event["updated_at"], "2026-07-13T02:00:01Z")
        self.assertEqual(self.service.get_evaluation(event["id"], "local_user"), event)
        self.assertEqual(self.service.list_evaluations("local_user"), [event])
        with self.assertRaisesRegex(ValueError, "Only a recorded blinded choice"):
            self.service.reveal_and_record_feedback(
                event["id"],
                "local_user",
                "2026-07-13T02:00:02Z",
                feels_like_me=4,
                usefulness=5,
                labels=[],
            )

    def test_tie_and_cannot_judge_do_not_fabricate_variant_choices(self) -> None:
        tie = self.create_evaluation(
            "eval_tie_v1",
            selection="tie",
            labels=[],
            affected_guidance_refs=[],
        )
        self.service.record_blinded_choice(
            "eval_cannot_v1",
            "local_user",
            self.run["id"],
            list(reversed(self.presented_order)),
            "cannot_judge",
            "2026-07-13T02:01:00Z",
        )
        cannot = self.service.reveal_and_record_feedback(
            "eval_cannot_v1",
            "local_user",
            "2026-07-13T02:01:01Z",
            feels_like_me=None,
            usefulness=None,
            labels=[],
            affected_guidance_refs=[],
        )
        self.assertEqual(tie["choice"], "tie")
        self.assertIsNone(tie["selected_variant_id"])
        self.assertEqual(cannot["choice"], "cannot_judge")
        self.assertIsNone(cannot["selected_variant_id"])
        self.assertIsNone(cannot["feels_like_me"])

    def test_unknown_unviewable_and_wrong_owner_runs_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown Style Kit pilot run"):
            self.service.record_blinded_choice(
                "eval_unknown_v1",
                "local_user",
                "run_missing_v1",
                self.presented_order,
                "tie",
                "2026-07-13T02:02:00Z",
            )
        with self.assertRaisesRegex(ValueError, "owner does not match"):
            self.service.record_blinded_choice(
                "eval_owner_v1",
                "other_user",
                self.run["id"],
                self.presented_order,
                "tie",
                "2026-07-13T02:02:00Z",
            )

        dry_run = self.pilot_service.create_run(
            "run_dry_evaluation_v1",
            "local_user",
            "2026-07-13T02:02:00Z",
            "project_description",
            "Write a short project description.",
            "professional",
            [self.guidance["id"]],
        )
        with self.assertRaisesRegex(ValueError, "active completed mock run"):
            self.service.record_blinded_choice(
                "eval_dry_v1",
                "local_user",
                dry_run["id"],
                [variant["variant_id"] for variant in dry_run["variants"]],
                "tie",
                "2026-07-13T02:03:00Z",
            )

    def test_presentation_ratings_labels_and_correction_boundaries(self) -> None:
        with self.assertRaisesRegex(ValueError, "each run variant exactly once"):
            self.service.record_blinded_choice(
                "eval_order_v1",
                "local_user",
                self.run["id"],
                [self.generic["variant_id"], self.generic["variant_id"]],
                self.generic["variant_id"],
                "2026-07-13T02:04:00Z",
            )
        with self.assertRaisesRegex(ValueError, "selection must be"):
            self.service.record_blinded_choice(
                "eval_selection_v1",
                "local_user",
                self.run["id"],
                self.presented_order,
                "variant_missing_v1",
                "2026-07-13T02:04:00Z",
            )
        self.service.record_blinded_choice(
            "eval_rating_v1",
            "local_user",
            self.run["id"],
            self.presented_order,
            "tie",
            "2026-07-13T02:04:00Z",
        )
        for invalid_rating in (0, 6, True, 4.5):
            with self.subTest(invalid_rating=invalid_rating):
                with self.assertRaisesRegex(ValueError, "integer from 1 through 5"):
                    self.service.reveal_and_record_feedback(
                        "eval_rating_v1",
                        "local_user",
                        "2026-07-13T02:04:01Z",
                        feels_like_me=invalid_rating,
                        usefulness=4,
                        labels=[],
                    )
        with self.assertRaisesRegex(ValueError, "labels must be unique"):
            self.create_evaluation("eval_duplicate_label_v1", labels=["useful", "useful"])
        with self.assertRaisesRegex(ValueError, "Unknown evaluation labels"):
            self.create_evaluation("eval_unknown_label_v1", labels=["perfect"])
        with self.assertRaisesRegex(ValueError, "require a correction"):
            self.create_evaluation("eval_no_correction_v1", labels=["wrong"], correction="  ")

    def test_affected_guidance_must_have_been_used_by_personalized_variant(self) -> None:
        with self.assertRaisesRegex(ValueError, "not used by the run"):
            self.create_evaluation(
                "eval_unused_guidance_v1",
                affected_guidance_refs=["guide_missing_v1"],
            )
        with self.assertRaisesRegex(ValueError, "must be unique"):
            self.create_evaluation(
                "eval_duplicate_guidance_v1",
                affected_guidance_refs=[self.guidance["id"], self.guidance["id"]],
            )

    def test_choice_and_reveal_timestamp_order_is_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "must include a timezone"):
            self.service.record_blinded_choice(
                "eval_time_zone_v1",
                "local_user",
                self.run["id"],
                self.presented_order,
                "tie",
                "2026-07-13T02:05:00",
            )
        self.service.record_blinded_choice(
            "eval_time_order_v1",
            "local_user",
            self.run["id"],
            self.presented_order,
            "tie",
            "2026-07-13T02:05:01Z",
        )
        with self.assertRaisesRegex(ValueError, "must be later"):
            self.service.reveal_and_record_feedback(
                "eval_time_order_v1",
                "local_user",
                "2026-07-13T02:05:01Z",
                feels_like_me=None,
                usefulness=None,
                labels=[],
            )

    def test_independent_deletion_redacts_feedback_without_mutating_evidence(self) -> None:
        assessment_before = ASSESSMENT_DB.read_bytes()
        protected_before = {
            collection: self.repository.list_records(collection)
            for collection in ("sources", "observations", "generation_guidance", "pilot_runs")
        }
        event = self.create_evaluation(
            labels=["too_strong"],
            correction="Use less forceful wording.",
        )
        for collection, records in protected_before.items():
            self.assertEqual(self.repository.list_records(collection), records)
        deleted = self.service.delete_evaluation(
            event["id"],
            "local_user",
            "2026-07-13T02:06:00Z",
        )
        self.assertEqual(deleted["evaluation_state"], "deleted")
        self.assertEqual(deleted["record_state"], "deleted")
        self.assertEqual(deleted["export_state"], "deleted")
        self.assertEqual(deleted["consent_refs"], [])
        self.assertEqual(deleted["presented_variant_order"], [])
        self.assertIsNone(deleted["choice"])
        self.assertIsNone(deleted["correction"])
        self.assertEqual(deleted["affected_guidance_refs"], [])
        self.assertIsNone(deleted["provenance"]["choice_recorded_at"])
        self.assertFalse(deleted["provenance"]["revealed_after_choice"])
        self.assertEqual(self.service.list_evaluations("local_user"), [])
        self.assertEqual(self.service.list_evaluations("local_user", include_deleted=True), [deleted])
        for collection, records in protected_before.items():
            self.assertEqual(self.repository.list_records(collection), records)
        self.assertEqual(ASSESSMENT_DB.read_bytes(), assessment_before)
        with self.assertRaisesRegex(ValueError, "already deleted"):
            self.service.delete_evaluation(event["id"], "local_user", "2026-07-13T02:07:00Z")


if __name__ == "__main__":
    unittest.main()
