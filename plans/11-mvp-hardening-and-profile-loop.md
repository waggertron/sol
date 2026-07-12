# MVP Hardening and Profile Loop Plan

## Purpose

Track the next implementation path after the local assessment web MVP:

1. browser QA and automated tests
2. profile atom editing
3. evidence and uncertainty views
4. scoped profile context export
5. first generation pilot

This plan is the active task ledger for turning the assessment MVP into a
reliable profile loop:

assessment -> score -> inspect -> correct -> export/use.

## Completed Baseline

- [x] Build the assessment-first CLI MVP.
  - Commit: `3b91ada`
  - Delivered scoring from stored instruments, JSONDB-backed session storage,
    assessment-derived profile atoms, sample responses, research promotion
    workflow, and profile atom lifecycle documentation.
- [x] Build the local assessment web MVP and profile workbench.
  - Commit: `74684b4`
  - Delivered local Python web server, static browser UI, assessment
    administration, autosave, scoring, result presentation, session
    export/delete, and cross-session atom review.

## Phase 1: Browser QA And Tests

Goal: make the current local MVP repeatable and verifiable before adding more
behavior.

Tasks:

- [x] Add focused tests for `tools/assessment_session_store.py`.
  - Commit: `b627a9f`
  - Cover create, save responses, score, list sessions, list profile atoms,
    review atom, export shape, and delete.
  - Use isolated temp JSONDB state rather than mutating the tracked
    `jsondb/assessment_sessions.json`.
- [x] Add focused tests for `tools/assessment_web_mvp.py` route behavior.
  - Commit: `b627a9f`
  - Cover health, manifest, instrument fetch, session create, response save,
    score, export, atom review, aggregate atoms, and delete.
  - Start the server on a test port or use handler-level tests if cleaner.
- [x] Add a static UI smoke test for the browser surface.
  - Commit: `b627a9f`
  - Verify Administer and Workbench tabs render.
  - Verify instrument list loads.
  - Verify session export/delete buttons enable only when a session is loaded.
  - Verify workbench session and atom sections render from API data.
  - Current coverage checks served HTML/JS and static UI contracts; full
    rendered-browser automation remains a later enhancement.
- [x] Add responsive layout checks for desktop and mobile widths.
  - Commit: `352e9f4`
  - Confirm no visible text overlap in the sidebar, topbar, questionnaire,
    session cards, atom cards, and action rows.
  - Commit `b627a9f` added static responsive CSS guard checks.
  - Commit `352e9f4` added rendered desktop/mobile screenshot capture for the
    Administer and Workbench views, with manual inspection of generated
    screenshots.
- [x] Add a local QA script or documented command set.
  - Commit: `b627a9f`
  - The script should compile Python, validate JS syntax, validate JSONDB, and
    run the route/browser smoke checks.
- [x] Document cleanup behavior.
  - Commit: `b627a9f`
  - Any generated QA sessions must be deleted automatically.
  - Any screenshots or temporary artifacts must live under an ignored local
    path.

Acceptance criteria:

- [x] A single local validation command can prove the assessment web MVP still
  works.
  - Commit: `b627a9f`
- [x] Tests do not leave persistent repo data changes.
  - Commit: `b627a9f`
- [x] The UI is visually usable on desktop and mobile widths.
  - Static responsive guards exist in commit `b627a9f`.
  - Rendered screenshot verification exists in commit `352e9f4`.

## Phase 2: Profile Atom Editing

Goal: let users correct profile atoms without losing provenance.

Tasks:

- [x] Extend the profile atom review contract with editable fields.
  - Add or document `original_claim`, edited `claim`, `user_note`, and
    `review_history`.
  - Preserve generated text as provenance when a user edits the claim.
- [x] Extend `review_atom` in the session store.
  - Support claim edits, notes, feedback state, activation scope, and timestamped
    history entries.
- [x] Add web API support for atom edits.
  - Keep edits session-scoped and atom-id scoped.
  - Return the updated atom after mutation.
- [x] Add UI controls for editing.
  - Inline edit or compact modal is acceptable.
  - User should be able to confirm, reject, keep review-only, edit claim text,
    and add a note.
- [x] Add tests for edit persistence and history.
  - Confirm edits survive reload and appear in the aggregate workbench.
- [x] Update docs.
  - Reflect edit semantics in profile atom output docs, session-storage docs,
    and web MVP docs.

Acceptance criteria:

- [x] A user can edit an atom claim and still inspect the original generated
  claim.
- [x] A user note can be stored without changing raw assessment responses.
- [x] Edited atoms remain non-diagnostic and user-visible.

## Phase 3: Evidence And Uncertainty Views

Goal: make every profile claim inspectable.

Tasks:

- [x] Add score evidence panels.
  - Show raw score, normalized score, score range, scoring method, and scale id.
- [x] Add item-level evidence expansion.
  - Show item ids, response values, keying direction, and reverse-scored status.
- [x] Add instrument/source context.
  - Show instrument name, construct system, license posture, source URL when
    available, and interpretation notes.
- [x] Add uncertainty/caution text.
  - Explain brief instrument limitations for TIPI.
  - Explain reliability-derived confidence for Mini-IPIP where available.
  - Keep neuroticism/emotional-stability language non-diagnostic.
- [x] Add evidence view tests.
  - Verify evidence appears for at least TIPI and Mini-IPIP sample sessions.
- [x] Update docs.
  - Document evidence display requirements and interpretation boundaries.

Acceptance criteria:

- [x] A user can answer why a score-derived atom exists.
- [x] A user can see the exact assessment evidence behind a claim.
- [x] The UI clearly distinguishes self-report evidence from identity facts.

## Phase 4: Scoped Profile Context Export

Goal: create the first profile packet that future generation flows can consume.

Tasks:

- [x] Define a profile context packet schema.
  - Include selected active/contextual atoms, confidence, evidence summaries,
    contraindications, and generation-safe language.
- [x] Add a session-store or profile-store helper to build the packet.
  - Default to confirmed/contextual atoms.
  - Exclude suppressed atoms.
  - Include review-only atoms only when explicitly requested.
- [x] Add a web API route for profile context export.
- [x] Add UI controls in the workbench.
  - Export confirmed/contextual profile context.
  - Optionally include provisional atoms for internal testing.
- [x] Add tests for export filtering.
- [x] Update docs.
  - Document what the packet can and cannot be used for.

Acceptance criteria:

- [x] The repo can produce a scoped profile context JSON packet.
- [x] Suppressed/rejected atoms are excluded by default.
- [x] The packet preserves uncertainty and source provenance.

## Phase 5: First Generation Pilot

Goal: close the first assess -> inspect -> correct -> use loop.

Tasks:

- [x] Choose one low-risk generation artifact.
  - Recommended first artifact: writing voice guide or communication style
    summary.
- [x] Add a local generation prompt template.
  - Input should be the scoped profile context packet.
  - Output should avoid diagnosis, protected traits, and fixed identity claims.
- [x] Add a local dry-run mode.
  - Render the prompt and context without calling any external model.
- [ ] Add a model-backed mode later only after the prompt contract is reviewed.
- [x] Add feedback capture.
  - Store whether output feels accurate, useful, too strong, too generic, or
    wrong.
- [x] Feed user feedback back into atom confidence or mapping notes.
- [x] Update docs.
  - Document pilot scope, risks, and evaluation criteria.

Acceptance criteria:

- [ ] A confirmed profile context packet can produce a first user-visible
  writing/communication artifact.
- [x] The user can evaluate and correct the output.
- [ ] Generation does not treat assessment scores as deterministic personality
  truth.

## Current Priority

Continue Phase 5 with a user-reviewed generation-guidance authoring path and
persisted pilot-run records. The prompt/feedback contract review is complete,
and the model-backed gate remains intentionally unapproved until the entry
conditions in `docs/architecture/assessments/generation-contract-review.md`
are satisfied.

## Latest Validation Evidence

- `./scripts/run_assessment_web_mvp_qa.sh`: 20 tests pass on Python 3.14.6;
  tracked `jsondb/assessment_sessions.json` remains unchanged.
- The same QA command cannot bind its isolated localhost server inside the
  Codex managed sandbox (`PermissionError: [Errno 1]`), but passes unchanged in
  the host shell. This is an execution-environment restriction, not an
  application failure.
- `./scripts/run_assessment_web_mvp_visual_qa.sh`: desktop and mobile Administer
  and Workbench captures pass against an isolated temporary session DB; manual
  inspection confirms the collapsed atom editor remains usable at both widths.

## 2026-07-12 Integrity Audit Follow-Up

- [x] Restore item-count confidence fallback logic and add boundary tests.
- [x] Validate response item IDs and response-scale values at the shared store.
- [x] Prevent reviewed atoms from being overwritten by rescoring.
- [x] Serialize local mutations and atomically replace JSONDB files.
- [x] Persist consent and exact instrument/scoring provenance for new sessions.
- [x] Enforce lifecycle state/scope/feedback invariants.
- [x] Add separate response/atom deletion with feedback-reference cleanup.
- [x] Refresh current corpus counts and document the integrity decision.

The full plan/progress audit lives at
`docs/audits/2026-07-12-initial-plan-progress-audit.md`.
