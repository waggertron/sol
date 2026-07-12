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
import style_kit_store as store


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


def eligible_profile_atom(atom_id: str = "assessment.sample.style.v0") -> dict:
    return {
        "id": atom_id,
        "state": "active_atom",
        "activation_scope": "contextual",
        "user_feedback": "confirmed",
        "sensitivity_level": "low",
        "claim": "Self-report evidence that still requires concrete user-reviewed guidance.",
    }


class StyleKitGuidanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db = os.environ.get(store.STYLE_KIT_DB_ENV)
        os.environ[store.STYLE_KIT_DB_ENV] = str(Path(self.tmp.name) / "style-kit-records.json")
        self.repository = store.JsonStyleKitRepository()
        self.bundle = load_valid_bundle()
        self.repository.create_record("sources", self.bundle["sources"][0])
        self.repository.create_record("observations", self.bundle["observations"][0])
        self.service = guidance.GuidanceService(self.repository)

    def tearDown(self) -> None:
        if self.previous_db is None:
            os.environ.pop(store.STYLE_KIT_DB_ENV, None)
        else:
            os.environ[store.STYLE_KIT_DB_ENV] = self.previous_db
        self.tmp.cleanup()

    def test_proposed_confirmed_disabled_lifecycle_and_filters(self) -> None:
        proposal = proposed_guidance(self.bundle)
        created = self.service.create_guidance(proposal)
        self.assertEqual(created["user_state"], "proposed")
        self.assertEqual(self.service.eligible_guidance("local_user"), [])

        confirmed = self.service.review_guidance(
            proposal["id"],
            "local_user",
            "2026-07-12T18:10:00-07:00",
            "confirmed",
        )
        self.assertEqual(confirmed["user_state"], "confirmed")
        self.assertEqual(confirmed["updated_at"], "2026-07-13T01:10:00Z")
        self.assertEqual(confirmed["provenance"]["guidance_version"], 2)
        self.assertEqual(confirmed["review_history"][-1]["changes"][-1]["to"], "confirmed")
        self.assertEqual(len(self.service.eligible_guidance("local_user")), 1)
        self.assertEqual(
            len(
                self.service.eligible_guidance(
                    "local_user",
                    context="professional",
                    task_scope="project_description",
                )
            ),
            1,
        )
        self.assertEqual(self.service.eligible_guidance("local_user", context="reflective"), [])
        self.assertEqual(self.service.eligible_guidance("other_user"), [])

        disabled = self.service.disable_guidance(
            proposal["id"],
            "local_user",
            "2026-07-13T01:11:00Z",
        )
        self.assertEqual(disabled["user_state"], "disabled")
        self.assertEqual(disabled["provenance"]["guidance_version"], 3)
        self.assertEqual(self.service.eligible_guidance("local_user"), [])

    def test_edits_preserve_original_and_append_prompt_safe_history(self) -> None:
        proposal = proposed_guidance(self.bundle)
        self.service.create_guidance(proposal)
        original = proposal["original_instruction"]
        edited = self.service.review_guidance(
            proposal["id"],
            "local_user",
            "2026-07-13T01:12:00Z",
            "edited",
            instruction="Prefer concise sentences and end with one concrete next step.",
            prompt_safe_instruction="Prefer concise sentences and end with one concrete next step.",
            contraindications=["Do not force brevity when the user asks for reflective detail."],
        )
        self.assertEqual(edited["original_instruction"], original)
        self.assertNotEqual(edited["instruction"], original)
        self.assertEqual(edited["user_state"], "edited")
        changed_fields = [change["field"] for change in edited["review_history"][0]["changes"]]
        self.assertEqual(
            changed_fields,
            ["instruction", "prompt_safe_instruction", "contraindications", "user_state"],
        )
        self.assertEqual(len(self.service.eligible_guidance("local_user")), 1)

    def test_supported_transition_matrix_is_explicit(self) -> None:
        direct_disable = proposed_guidance(self.bundle, "guide_direct_disable_v1")
        self.service.create_guidance(direct_disable)
        disabled = self.service.disable_guidance(
            direct_disable["id"],
            "local_user",
            "2026-07-13T01:12:10Z",
        )
        self.assertEqual(disabled["user_state"], "disabled")
        with self.assertRaisesRegex(ValueError, "disabled -> confirmed"):
            self.service.review_guidance(
                direct_disable["id"],
                "local_user",
                "2026-07-13T01:12:20Z",
                "confirmed",
            )

        repeat_edit = proposed_guidance(self.bundle, "guide_repeat_edit_v1")
        self.service.create_guidance(repeat_edit)
        first_edit = self.service.review_guidance(
            repeat_edit["id"],
            "local_user",
            "2026-07-13T01:12:30Z",
            "edited",
            instruction="Use concise sentences with one clear next step.",
            prompt_safe_instruction="Use concise sentences with one clear next step.",
        )
        second_edit = self.service.review_guidance(
            repeat_edit["id"],
            "local_user",
            "2026-07-13T01:12:40Z",
            "edited",
            contexts=["professional", "public"],
        )
        self.assertEqual(first_edit["user_state"], "edited")
        self.assertEqual(second_edit["user_state"], "edited")
        self.assertEqual(len(second_edit["review_history"]), 2)
        self.assertEqual(
            self.service.disable_guidance(
                repeat_edit["id"],
                "local_user",
                "2026-07-13T01:12:50Z",
            )["user_state"],
            "disabled",
        )

        confirmed_edit = proposed_guidance(self.bundle, "guide_confirmed_edit_v1")
        self.service.create_guidance(confirmed_edit)
        self.service.review_guidance(
            confirmed_edit["id"],
            "local_user",
            "2026-07-13T01:13:00Z",
            "confirmed",
        )
        edited = self.service.review_guidance(
            confirmed_edit["id"],
            "local_user",
            "2026-07-13T01:13:10Z",
            "edited",
            contraindications=["Keep this scoped to professional writing."],
        )
        self.assertEqual(edited["user_state"], "edited")
        self.assertEqual(len(edited["review_history"]), 2)

    def test_invalid_transitions_and_edits_do_not_change_storage(self) -> None:
        confirmed_input = proposed_guidance(self.bundle)
        confirmed_input["user_state"] = "confirmed"
        with self.assertRaisesRegex(ValueError, "must start proposed"):
            self.service.create_guidance(confirmed_input)

        proposal = proposed_guidance(self.bundle)
        self.service.create_guidance(proposal)
        original_bytes = self.repository.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "owner does not match"):
            self.service.review_guidance(proposal["id"], "other_user", "2026-07-13T01:13:00Z", "confirmed")
        with self.assertRaisesRegex(ValueError, "must be later"):
            self.service.review_guidance(proposal["id"], "local_user", "2026-07-12T18:01:00Z", "confirmed")
        with self.assertRaisesRegex(ValueError, "require a separate prompt_safe_instruction"):
            self.service.review_guidance(
                proposal["id"],
                "local_user",
                "2026-07-13T01:13:00Z",
                "edited",
                instruction="Change only the raw instruction.",
            )
        with self.assertRaisesRegex(ValueError, "requires at least one material"):
            self.service.review_guidance(proposal["id"], "local_user", "2026-07-13T01:13:00Z", "edited")
        with self.assertRaisesRegex(ValueError, "cannot include edits"):
            self.service.review_guidance(
                proposal["id"],
                "local_user",
                "2026-07-13T01:13:00Z",
                "confirmed",
                contexts=["professional", "public"],
            )
        self.assertEqual(self.repository.path.read_bytes(), original_bytes)

        self.service.review_guidance(proposal["id"], "local_user", "2026-07-13T01:14:00Z", "confirmed")
        with self.assertRaisesRegex(ValueError, "confirmed -> confirmed"):
            self.service.review_guidance(proposal["id"], "local_user", "2026-07-13T01:15:00Z", "confirmed")

    def test_observation_must_be_confirmed_and_remain_eligible(self) -> None:
        observation = copy.deepcopy(self.bundle["observations"][0])
        observation["review_state"] = "proposed"
        self.repository.replace_record("observations", observation["id"], observation)
        proposal = proposed_guidance(self.bundle)
        self.service.create_guidance(proposal)
        with self.assertRaisesRegex(ValueError, "not user-confirmed"):
            self.service.review_guidance(proposal["id"], "local_user", "2026-07-13T01:16:00Z", "confirmed")

        observation["review_state"] = "confirmed"
        self.repository.replace_record("observations", observation["id"], observation)
        self.service.review_guidance(proposal["id"], "local_user", "2026-07-13T01:17:00Z", "confirmed")
        self.assertEqual(len(self.service.eligible_guidance("local_user")), 1)

        observation["review_state"] = "rejected"
        self.repository.replace_record("observations", observation["id"], observation)
        self.assertEqual(self.service.eligible_guidance("local_user"), [])

        blocked = proposed_guidance(self.bundle, "guide_blocked_v1")
        observation["review_state"] = "proposed"
        observation["sensitivity_level"] = "blocked"
        self.repository.replace_record("observations", observation["id"], observation)
        with self.assertRaisesRegex(ValueError, "sensitivity is not eligible"):
            self.service.create_guidance(blocked)

    def test_profile_atoms_are_optional_evidence_but_never_auto_activate_guidance(self) -> None:
        atom = eligible_profile_atom()
        atoms = {atom["id"]: atom}
        service = guidance.GuidanceService(self.repository, atoms.get)
        proposal = proposed_guidance(self.bundle, "guide_atom_v1")
        proposal["observation_refs"] = []
        proposal["profile_atom_refs"] = [atom["id"]]
        proposal["provenance"]["created_by"] = "deterministic_mapping"
        created = service.create_guidance(proposal)
        self.assertEqual(created["user_state"], "proposed")
        self.assertEqual(service.eligible_guidance("local_user"), [])

        invalid_atom_states = [
            {"state": "provisional_atom", "activation_scope": "review_only"},
            {"state": "suppressed_atom", "activation_scope": "review_only"},
            {"activation_scope": "review_only"},
            {"user_feedback": "rejected"},
            {"sensitivity_level": "blocked"},
        ]
        original_atom = copy.deepcopy(atom)
        for changes in invalid_atom_states:
            with self.subTest(changes=changes):
                atoms[atom["id"]] = {**original_atom, **changes}
                with self.assertRaisesRegex(ValueError, "not generation-eligible"):
                    service.review_guidance(
                        proposal["id"],
                        "local_user",
                        "2026-07-13T01:18:00Z",
                        "confirmed",
                    )

        atoms[atom["id"]] = original_atom
        confirmed = service.review_guidance(
            proposal["id"],
            "local_user",
            "2026-07-13T01:19:00Z",
            "confirmed",
        )
        self.assertEqual(confirmed["user_state"], "confirmed")
        self.assertEqual(atoms[atom["id"]], original_atom)
        self.assertEqual(len(service.eligible_guidance("local_user")), 1)

    def test_missing_or_ineligible_evidence_is_an_explicit_creation_error(self) -> None:
        missing = proposed_guidance(self.bundle, "guide_missing_v1")
        missing["observation_refs"] = []
        with self.assertRaisesRegex(ValueError, "must reference"):
            self.service.create_guidance(missing)

        atom_only = proposed_guidance(self.bundle, "guide_unresolved_atom_v1")
        atom_only["observation_refs"] = []
        atom_only["profile_atom_refs"] = ["assessment.missing.v0"]
        with self.assertRaisesRegex(ValueError, "not generation-eligible"):
            self.service.create_guidance(atom_only)


if __name__ == "__main__":
    unittest.main()
