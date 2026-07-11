import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if TOOLS.as_posix() not in sys.path:
    sys.path.insert(0, TOOLS.as_posix())

import assessment_session_store as store


TIPI_PATH = ROOT / "assessments" / "ocean" / "instruments" / "tipi.json"


def valid_tipi_responses() -> dict[str, int]:
    responses = {
        "tipi:item:001": 6,
        "tipi:item:002": 2,
        "tipi:item:003": 6,
        "tipi:item:004": 3,
        "tipi:item:005": 7,
        "tipi:item:006": 2,
        "tipi:item:007": 6,
        "tipi:item:008": 2,
        "tipi:item:009": 6,
        "tipi:item:010": 2,
    }
    assert len(responses) == 10
    assert all(1 <= value <= 7 for value in responses.values())
    return responses


class AssessmentSessionStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db = os.environ.get(store.SESSIONS_DB_ENV)
        os.environ[store.SESSIONS_DB_ENV] = str(Path(self.tmp.name) / "assessment_sessions.json")

    def tearDown(self) -> None:
        if self.previous_db is None:
            os.environ.pop(store.SESSIONS_DB_ENV, None)
        else:
            os.environ[store.SESSIONS_DB_ENV] = self.previous_db
        self.tmp.cleanup()

    def test_session_lifecycle_uses_isolated_jsondb(self) -> None:
        session = store.create_session(
            "test_tipi_session",
            TIPI_PATH.as_posix(),
            "2026-07-08T22:00:00Z",
        )
        self.assertEqual(session["status"], "in_progress")
        self.assertEqual(session["instrument_id"], "tipi")

        updated = store.save_response_map("test_tipi_session", valid_tipi_responses(), merge=False)
        self.assertEqual(len(updated["responses"]), 10)

        scored = store.score_session("test_tipi_session", "2026-07-08T22:05:00Z")
        self.assertEqual(scored["status"], "completed")
        self.assertEqual(len(scored["scores"]), 5)
        self.assertEqual(len(scored["profile_atoms"]), 5)
        self.assertTrue(all(atom["state"] == "provisional_atom" for atom in scored["profile_atoms"]))
        self.assertTrue(all(atom["original_claim"] == atom["claim"] for atom in scored["profile_atoms"]))
        self.assertTrue(all(atom["review_history"] == [] for atom in scored["profile_atoms"]))

        listed = store.list_sessions()
        self.assertEqual(listed["session_count"], 1)
        self.assertEqual(listed["sessions"][0]["response_count"], 10)
        self.assertEqual(listed["sessions"][0]["profile_atom_count"], 5)

        atoms = store.list_profile_atoms()
        self.assertEqual(atoms["atom_count"], 5)
        self.assertEqual({atom["session_id"] for atom in atoms["atoms"]}, {"test_tipi_session"})

        reviewed = store.review_atom(
            "test_tipi_session",
            "assessment.tipi.tipi_extraversion.v0",
            "2026-07-08T22:06:00Z",
            user_feedback="confirmed",
            state="active_atom",
            activation_scope="contextual",
        )
        self.assertEqual(reviewed["user_feedback"], "confirmed")
        self.assertEqual(reviewed["state"], "active_atom")
        self.assertEqual(reviewed["activation_scope"], "contextual")
        self.assertEqual(len(reviewed["review_history"]), 1)

        original_responses = dict(scored["responses"])
        original_claim = reviewed["original_claim"]
        edited = store.review_atom(
            "test_tipi_session",
            "assessment.tipi.tipi_extraversion.v0",
            "2026-07-08T22:07:00Z",
            user_feedback="edited",
            claim="I often feel energized by social interaction, depending on context.",
            user_note="This is stronger with close friends than in large groups.",
        )
        self.assertEqual(edited["original_claim"], original_claim)
        self.assertNotEqual(edited["claim"], original_claim)
        self.assertEqual(edited["user_feedback"], "edited")
        self.assertEqual(len(edited["review_history"]), 2)
        self.assertEqual(
            edited["review_history"][-1]["changes"]["claim"]["from"],
            original_claim,
        )

        reloaded = store.show_session("test_tipi_session")
        reloaded_atom = store.find_atom(reloaded, "assessment.tipi.tipi_extraversion.v0")
        self.assertEqual(reloaded_atom["user_note"], "This is stronger with close friends than in large groups.")
        self.assertEqual(reloaded["responses"], original_responses)

        aggregate_atom = next(
            atom
            for atom in store.list_profile_atoms()["atoms"]
            if atom["id"] == "assessment.tipi.tipi_extraversion.v0"
        )
        self.assertEqual(aggregate_atom["claim"], edited["claim"])
        self.assertEqual(len(aggregate_atom["review_history"]), 2)

        shown = store.show_session("test_tipi_session")
        self.assertEqual(shown["profile_atoms"][0]["source_ids"][1], "assessment_session:test_tipi_session")

        deleted = store.delete_session("test_tipi_session")
        self.assertEqual(deleted["session_id"], "test_tipi_session")
        self.assertEqual(store.list_sessions()["session_count"], 0)

    def test_unknown_session_errors_are_explicit(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown session"):
            store.show_session("missing")
        with self.assertRaisesRegex(ValueError, "Unknown session"):
            store.delete_session("missing")

    def test_atom_review_rejects_out_of_contract_values(self) -> None:
        store.create_session("invalid_review", TIPI_PATH.as_posix(), "2026-07-08T22:00:00Z")
        store.save_response_map("invalid_review", valid_tipi_responses(), merge=False)
        store.score_session("invalid_review", "2026-07-08T22:05:00Z")
        atom_id = "assessment.tipi.tipi_extraversion.v0"

        with self.assertRaisesRegex(ValueError, "Invalid atom state"):
            store.review_atom("invalid_review", atom_id, "2026-07-08T22:06:00Z", state="diagnosed")
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            store.review_atom("invalid_review", atom_id, "2026-07-08T22:06:00Z", claim="   ")


if __name__ == "__main__":
    unittest.main()
