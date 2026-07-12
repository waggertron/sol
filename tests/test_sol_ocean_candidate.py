import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if TOOLS.as_posix() not in sys.path:
    sys.path.insert(0, TOOLS.as_posix())

import validate_sol_ocean_candidate as validator
import assessment_session_store as store
import assessment_to_profile_atoms as generator


CANDIDATE_PATH = ROOT / "assessments" / "ocean" / "experimental" / "sol_ocean_quick_v0.json"
MANIFEST_PATH = ROOT / "assessments" / "ocean" / "manifest.json"


class SolOceanCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db = os.environ.get(store.SESSIONS_DB_ENV)
        os.environ[store.SESSIONS_DB_ENV] = str(Path(self.tmp.name) / "assessment_sessions.json")
        self.candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
        self.comparison_texts = validator.stored_item_texts(ROOT / "assessments" / "ocean" / "instruments")

    def tearDown(self) -> None:
        if self.previous_db is None:
            os.environ.pop(store.SESSIONS_DB_ENV, None)
        else:
            os.environ[store.SESSIONS_DB_ENV] = self.previous_db
        self.tmp.cleanup()

    def test_candidate_contract_and_collision_check_pass(self) -> None:
        errors = validator.validate_candidate(self.candidate, self.comparison_texts)
        self.assertEqual(errors, [])
        items = self.candidate["items"]
        self.assertEqual(len(items), 30)
        self.assertEqual({item["source_order"] for item in items}, set(range(1, 31)))
        self.assertEqual({item["keyed"] for item in items}, {"positive", "negative"})
        self.assertTrue(all(item["expected_failure_modes"] for item in items))

    def test_candidate_is_not_in_administrable_manifest(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        ids = {instrument["id"] for instrument in manifest["instruments"]}
        self.assertNotIn(self.candidate["id"], ids)
        with self.assertRaisesRegex(ValueError, "cannot enter the product scoring flow"):
            generator.generate_output(self.candidate, {}, "blocked_candidate", "2026-07-12T00:00:00Z")
        with self.assertRaisesRegex(ValueError, "cannot enter the product scoring flow"):
            store.create_session(
                "blocked_candidate",
                CANDIDATE_PATH.as_posix(),
                "2026-07-12T00:00:00Z",
                "2026-07-12T00:00:00Z",
            )

    def test_invalid_candidate_fixtures_fail_explicitly(self) -> None:
        invalid_keying = copy.deepcopy(self.candidate)
        invalid_keying["items"][0]["keyed"] = "sometimes"
        self.assertTrue(
            any("invalid keying" in error for error in validator.validate_candidate(invalid_keying, set()))
        )

        copied_wording = copy.deepcopy(self.candidate)
        copied_wording["items"][0]["text"] = "Extraverted, enthusiastic."
        self.assertTrue(
            any("exactly collides" in error for error in validator.validate_candidate(copied_wording, self.comparison_texts))
        )

        missing_metadata = copy.deepcopy(self.candidate)
        del missing_metadata["items"][0]["expected_failure_modes"]
        self.assertTrue(
            any("missing fields" in error for error in validator.validate_candidate(missing_metadata, set()))
        )


if __name__ == "__main__":
    unittest.main()
