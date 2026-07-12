#!/usr/bin/env python3
"""Serve the local assessment-first MVP as a small browser app."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from assessment_session_store import (
    create_session,
    build_profile_context,
    delete_session,
    delete_session_profile_atoms,
    delete_session_responses,
    list_profile_atoms,
    list_sessions,
    record_generation_feedback,
    review_atom,
    save_response_map,
    score_session,
    show_session,
)
from assessment_to_profile_atoms import load_json


ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "app" / "assessment-mvp"
ASSESSMENTS_DIR = ROOT / "assessments" / "ocean"
INSTRUMENTS_DIR = ASSESSMENTS_DIR / "instruments"
MANIFEST_PATH = ASSESSMENTS_DIR / "manifest.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def session_suffix() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def manifest_payload() -> dict:
    manifest = load_json(MANIFEST_PATH)
    entries = []
    for entry in manifest.get("instruments", []):
        instrument_id = entry["id"]
        path = ASSESSMENTS_DIR / entry["path"]
        if not path:
            continue
        instrument = load_json(path)
        entries.append(
            {
                "id": instrument["id"],
                "name": instrument["name"],
                "family": instrument.get("family"),
                "construct_system": instrument.get("construct_system"),
                "item_count": len(instrument.get("items", []))
                or sum(len(scale.get("items", [])) for scale in instrument.get("scales", [])),
                "scale_count": len(instrument.get("scales", [])),
                "license_status": instrument.get("license", {}).get("status"),
                "notes": instrument.get("notes", []),
                "response_scale_type": instrument.get("response_scale", {}).get("type"),
            }
        )
    return {
        "description": manifest.get("description"),
        "instrument_count": len(entries),
        "instruments": entries,
    }


def instrument_payload(instrument_id: str) -> dict:
    path = INSTRUMENTS_DIR / f"{instrument_id}.json"
    if not path.exists():
        raise FileNotFoundError(instrument_id)
    instrument = load_json(path)
    instrument["item_count"] = len(instrument.get("items", [])) or sum(
        len(scale.get("items", [])) for scale in instrument.get("scales", [])
    )
    return instrument


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def json_download_response(handler: BaseHTTPRequestHandler, filename: str, payload: dict) -> None:
    body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Disposition", f'attachment; filename="{filename}"')
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def text_response(handler: BaseHTTPRequestHandler, status: int, content_type: str, body: bytes) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json_body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length > 0 else b"{}"
    return json.loads(raw.decode("utf-8"))


class AssessmentHandler(BaseHTTPRequestHandler):
    server_version = "SolAssessmentMVP/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/health":
            json_response(self, HTTPStatus.OK, {"status": "ok", "time": now_iso()})
            return
        if path == "/api/manifest":
            json_response(self, HTTPStatus.OK, manifest_payload())
            return
        if path == "/api/sessions":
            json_response(self, HTTPStatus.OK, list_sessions())
            return
        if path == "/api/profile-atoms":
            json_response(self, HTTPStatus.OK, list_profile_atoms())
            return
        if path == "/api/profile-context":
            query = parse_qs(parsed.query)
            include_review_only = query.get("include_review_only", ["false"])[0].lower() == "true"
            json_download_response(
                self,
                "sol-profile-context.json",
                build_profile_context(now_iso(), include_review_only=include_review_only),
            )
            return
        if path.startswith("/api/instruments/"):
            instrument_id = unquote(path.removeprefix("/api/instruments/"))
            try:
                json_response(self, HTTPStatus.OK, instrument_payload(instrument_id))
            except FileNotFoundError:
                json_response(self, HTTPStatus.NOT_FOUND, {"error": f"Unknown instrument: {instrument_id}"})
            return
        if path.startswith("/api/sessions/") and path.endswith("/export"):
            session_id = unquote(path.removeprefix("/api/sessions/").removesuffix("/export"))
            try:
                json_download_response(self, f"{session_id}.json", show_session(session_id))
            except ValueError as exc:
                json_response(self, HTTPStatus.NOT_FOUND, {"error": str(exc)})
            return
        if path.startswith("/api/sessions/"):
            session_id = unquote(path.removeprefix("/api/sessions/"))
            try:
                json_response(self, HTTPStatus.OK, show_session(session_id))
            except ValueError as exc:
                json_response(self, HTTPStatus.NOT_FOUND, {"error": str(exc)})
            return
        self.serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/api/sessions":
                payload = read_json_body(self)
                instrument_id = payload["instrument_id"]
                started_at = payload.get("started_at") or now_iso()
                consent_at = payload.get("consent_at")
                user_id = payload.get("user_id")
                session_id = payload.get("session_id") or f"web_{instrument_id}_{session_suffix()}"
                session = create_session(
                    session_id=session_id,
                    instrument_path=(INSTRUMENTS_DIR / f"{instrument_id}.json").as_posix(),
                    started_at=started_at,
                    consent_at=consent_at,
                    user_id=user_id,
                )
                json_response(self, HTTPStatus.CREATED, session)
                return
            if path == "/api/generation-feedback":
                payload = read_json_body(self)
                event = record_generation_feedback(
                    event_id=payload["event_id"],
                    pilot_id=payload["pilot_id"],
                    recorded_at=payload.get("recorded_at") or now_iso(),
                    feedback=payload["feedback"],
                    atom_refs=payload["atom_refs"],
                    note=payload.get("note", ""),
                )
                json_response(self, HTTPStatus.CREATED, event)
                return
            if path.endswith("/responses"):
                session_id = unquote(path.removeprefix("/api/sessions/").removesuffix("/responses"))
                payload = read_json_body(self)
                session = save_response_map(session_id, payload.get("responses", {}), merge=payload.get("merge", True))
                json_response(self, HTTPStatus.OK, session)
                return
            if path.endswith("/score"):
                session_id = unquote(path.removeprefix("/api/sessions/").removesuffix("/score"))
                payload = read_json_body(self)
                session = score_session(session_id, payload.get("completed_at") or now_iso())
                json_response(self, HTTPStatus.OK, session)
                return
            if path.endswith("/review-atom"):
                session_id = unquote(path.removeprefix("/api/sessions/").removesuffix("/review-atom"))
                payload = read_json_body(self)
                atom = review_atom(
                    session_id=session_id,
                    atom_id=payload["atom_id"],
                    reviewed_at=payload.get("reviewed_at") or now_iso(),
                    user_feedback=payload.get("user_feedback"),
                    state=payload.get("state"),
                    activation_scope=payload.get("activation_scope"),
                    claim=payload.get("claim"),
                    user_note=payload.get("user_note"),
                )
                json_response(self, HTTPStatus.OK, atom)
                return
        except FileNotFoundError as exc:
            json_response(self, HTTPStatus.NOT_FOUND, {"error": f"Missing file: {exc}"})
            return
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        json_response(self, HTTPStatus.NOT_FOUND, {"error": f"Unknown route: {path}"})

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if path.startswith("/api/sessions/") and path.endswith("/responses"):
            session_id = unquote(path.removeprefix("/api/sessions/").removesuffix("/responses"))
            try:
                json_response(self, HTTPStatus.OK, delete_session_responses(session_id, now_iso()))
            except ValueError as exc:
                json_response(self, HTTPStatus.NOT_FOUND, {"error": str(exc)})
            return
        if path.startswith("/api/sessions/") and path.endswith("/profile-atoms"):
            session_id = unquote(path.removeprefix("/api/sessions/").removesuffix("/profile-atoms"))
            try:
                json_response(self, HTTPStatus.OK, delete_session_profile_atoms(session_id, now_iso()))
            except ValueError as exc:
                json_response(self, HTTPStatus.NOT_FOUND, {"error": str(exc)})
            return
        if path.startswith("/api/sessions/"):
            session_id = unquote(path.removeprefix("/api/sessions/"))
            try:
                json_response(self, HTTPStatus.OK, {"deleted": delete_session(session_id)})
            except ValueError as exc:
                json_response(self, HTTPStatus.NOT_FOUND, {"error": str(exc)})
            return
        json_response(self, HTTPStatus.NOT_FOUND, {"error": f"Unknown route: {path}"})

    def log_message(self, format: str, *args) -> None:
        return

    def serve_static(self, path: str) -> None:
        rel = "index.html" if path in {"/", ""} else path.lstrip("/")
        file_path = APP_DIR / rel
        if not file_path.exists() or not file_path.is_file():
            json_response(self, HTTPStatus.NOT_FOUND, {"error": f"Unknown route: {path}"})
            return

        content_type = "text/plain; charset=utf-8"
        if file_path.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif file_path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif file_path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"

        text_response(self, HTTPStatus.OK, content_type, file_path.read_bytes())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the local Sol assessment MVP.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), AssessmentHandler)
    print(json.dumps({"url": f"http://{args.host}:{args.port}", "status": "serving"}, indent=2))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
