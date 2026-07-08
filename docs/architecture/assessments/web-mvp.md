# Assessment Web MVP

This document defines the first local browser-facing implementation for the
assessment-first MVP.

## Goal

Provide a minimal UI that uses the existing repository assets directly:

- instrument manifest from `assessments/ocean/manifest.json`
- instrument JSON from `assessments/ocean/instruments/*.json`
- session persistence from `jsondb/assessment_sessions.json`
- scoring and profile-atom derivation from the existing Python tools

## Implementation

The web MVP consists of:

- `tools/assessment_web_mvp.py` - local HTTP server and JSON API
- `app/assessment-mvp/index.html` - browser UI shell
- `app/assessment-mvp/styles.css` - local styling
- `app/assessment-mvp/app.js` - client-side workflow

## Supported Flow

1. Load manifest and choose an instrument.
2. Require a local consent acknowledgment.
3. Start a session in the shared JSONDB store.
4. Render all assessment items from stored JSON.
5. Autosave responses into the active session.
6. Score the session through the existing scoring contract.
7. Display scores and derived profile atoms.
8. Allow confirm/reject/review-only atom state changes.
9. Resume a prior session by session id.
10. Export a session as JSON.
11. Delete a session from local JSONDB storage.
12. Review profile atoms across stored sessions in the workbench view.

## API Surface

- `GET /api/health`
- `GET /api/manifest`
- `GET /api/instruments/<instrument_id>`
- `GET /api/sessions`
- `POST /api/sessions`
- `GET /api/sessions/<session_id>`
- `GET /api/sessions/<session_id>/export`
- `POST /api/sessions/<session_id>/responses`
- `POST /api/sessions/<session_id>/score`
- `POST /api/sessions/<session_id>/review-atom`
- `DELETE /api/sessions/<session_id>`
- `GET /api/profile-atoms`

## Local Run

```bash
python3 tools/assessment_web_mvp.py --port 8765
```

Open `http://127.0.0.1:8765`.

## Boundaries

- This is a local-only MVP, not a deployed service.
- It intentionally uses the current JSONDB store directly.
- It is suitable for exploratory product development, not multi-user production
  operation.
- It does not yet implement authentication or access controls.
