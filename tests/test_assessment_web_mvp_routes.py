import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import request
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if TOOLS.as_posix() not in sys.path:
    sys.path.insert(0, TOOLS.as_posix())

import assessment_session_store as store
from assessment_web_mvp import AssessmentHandler


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


class AssessmentWebMvpRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db = os.environ.get(store.SESSIONS_DB_ENV)
        os.environ[store.SESSIONS_DB_ENV] = str(Path(self.tmp.name) / "assessment_sessions.json")
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), AssessmentHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()
        if self.previous_db is None:
            os.environ.pop(store.SESSIONS_DB_ENV, None)
        else:
            os.environ[store.SESSIONS_DB_ENV] = self.previous_db
        self.tmp.cleanup()

    def get_json(self, path: str) -> tuple[dict, request.addinfourl]:
        response = request.urlopen(f"{self.base_url}{path}", timeout=5)
        return json.loads(response.read().decode("utf-8")), response

    def post_json(self, path: str, payload: dict) -> tuple[dict, request.addinfourl]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        response = request.urlopen(req, timeout=5)
        return json.loads(response.read().decode("utf-8")), response

    def delete_json(self, path: str) -> dict:
        req = request.Request(f"{self.base_url}{path}", method="DELETE")
        response = request.urlopen(req, timeout=5)
        return json.loads(response.read().decode("utf-8"))

    def test_static_ui_routes_are_served(self) -> None:
        response = request.urlopen(f"{self.base_url}/", timeout=5)
        html = response.read().decode("utf-8")
        self.assertIn("nav-workbench", html)
        self.assertIn("export-current-session", html)
        self.assertIn("delete-current-session", html)
        self.assertIn("export-profile-context", html)

        script = request.urlopen(f"{self.base_url}/app.js", timeout=5).read().decode("utf-8")
        self.assertIn("loadWorkbench", script)
        self.assertIn("exportSession", script)
        self.assertIn("deleteSessionById", script)
        self.assertIn("exportProfileContext", script)

    def test_full_route_lifecycle_uses_isolated_jsondb(self) -> None:
        health, _ = self.get_json("/api/health")
        self.assertEqual(health["status"], "ok")

        manifest, _ = self.get_json("/api/manifest")
        self.assertEqual(manifest["instrument_count"], 11)

        instrument, _ = self.get_json("/api/instruments/tipi")
        self.assertEqual(instrument["id"], "tipi")
        self.assertEqual(instrument["item_count"], 10)

        created, _ = self.post_json(
            "/api/sessions",
            {
                "session_id": "route_test_tipi_session",
                "instrument_id": "tipi",
                "started_at": "2026-07-08T22:00:00Z",
            },
        )
        self.assertEqual(created["status"], "in_progress")

        saved, _ = self.post_json(
            "/api/sessions/route_test_tipi_session/responses",
            {"responses": valid_tipi_responses(), "merge": False},
        )
        self.assertEqual(len(saved["responses"]), 10)

        scored, _ = self.post_json(
            "/api/sessions/route_test_tipi_session/score",
            {"completed_at": "2026-07-08T22:05:00Z"},
        )
        self.assertEqual(scored["status"], "completed")
        self.assertEqual(len(scored["profile_atoms"]), 5)
        self.assertEqual(len(scored["scores"][0]["item_evidence"]), 2)
        self.assertIn("uncertainty_note", scored["profile_atoms"][0]["assessment_metadata"])

        exported, export_response = self.get_json("/api/sessions/route_test_tipi_session/export")
        self.assertEqual(exported["session_id"], "route_test_tipi_session")
        self.assertIn("attachment", export_response.headers["Content-Disposition"])

        reviewed, _ = self.post_json(
            "/api/sessions/route_test_tipi_session/review-atom",
            {
                "atom_id": "assessment.tipi.tipi_extraversion.v0",
                "reviewed_at": "2026-07-08T22:06:00Z",
                "user_feedback": "confirmed",
                "state": "active_atom",
                "activation_scope": "contextual",
            },
        )
        self.assertEqual(reviewed["state"], "active_atom")

        edited, _ = self.post_json(
            "/api/sessions/route_test_tipi_session/review-atom",
            {
                "atom_id": "assessment.tipi.tipi_extraversion.v0",
                "reviewed_at": "2026-07-08T22:07:00Z",
                "user_feedback": "edited",
                "claim": "I tend to be socially engaged in familiar settings.",
                "user_note": "Context matters to me.",
            },
        )
        self.assertEqual(edited["user_feedback"], "edited")
        self.assertEqual(edited["user_note"], "Context matters to me.")
        self.assertNotEqual(edited["original_claim"], edited["claim"])
        self.assertEqual(len(edited["review_history"]), 2)

        atom_payload, _ = self.get_json("/api/profile-atoms")
        self.assertEqual(atom_payload["atom_count"], 5)
        self.assertEqual(atom_payload["atoms"][0]["session_id"], "route_test_tipi_session")
        self.assertEqual(atom_payload["atoms"][0]["user_note"], "Context matters to me.")

        sessions, _ = self.get_json("/api/sessions")
        self.assertEqual(sessions["session_count"], 1)
        self.assertEqual(sessions["sessions"][0]["active_atom_count"], 1)

        profile_context, context_response = self.get_json("/api/profile-context")
        self.assertEqual(profile_context["atom_count"], 1)
        self.assertTrue(profile_context["atoms"][0]["eligible_for_generation"])
        self.assertIn("attachment", context_response.headers["Content-Disposition"])

        internal_context, _ = self.get_json("/api/profile-context?include_review_only=true")
        self.assertEqual(internal_context["atom_count"], 5)
        self.assertEqual(
            sum(1 for atom in internal_context["atoms"] if not atom["eligible_for_generation"]),
            4,
        )

        deleted = self.delete_json("/api/sessions/route_test_tipi_session")
        self.assertEqual(deleted["deleted"]["session_id"], "route_test_tipi_session")
        sessions_after_delete, _ = self.get_json("/api/sessions")
        self.assertEqual(sessions_after_delete["session_count"], 0)

    def test_missing_session_returns_404(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self.get_json("/api/sessions/missing")
        self.assertEqual(ctx.exception.code, 404)
        ctx.exception.close()


if __name__ == "__main__":
    unittest.main()
