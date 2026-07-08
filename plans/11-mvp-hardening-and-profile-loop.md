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

- [ ] Add focused tests for `tools/assessment_session_store.py`.
  - Cover create, save responses, score, list sessions, list profile atoms,
    review atom, export shape, and delete.
  - Use isolated temp JSONDB state rather than mutating the tracked
    `jsondb/assessment_sessions.json`.
- [ ] Add focused tests for `tools/assessment_web_mvp.py` route behavior.
  - Cover health, manifest, instrument fetch, session create, response save,
    score, export, atom review, aggregate atoms, and delete.
  - Start the server on a test port or use handler-level tests if cleaner.
- [ ] Add a browser smoke test for the static UI.
  - Verify Administer and Workbench tabs render.
  - Verify instrument list loads.
  - Verify session export/delete buttons enable only when a session is loaded.
  - Verify workbench session and atom sections render from API data.
- [ ] Add responsive layout checks for desktop and mobile widths.
  - Confirm no visible text overlap in the sidebar, topbar, questionnaire,
    session cards, atom cards, and action rows.
- [ ] Add a local QA script or documented command set.
  - The script should compile Python, validate JS syntax, validate JSONDB, and
    run the route/browser smoke checks.
- [ ] Document cleanup behavior.
  - Any generated QA sessions must be deleted automatically.
  - Any screenshots or temporary artifacts must live under an ignored local
    path.

Acceptance criteria:

- [ ] A single local validation command can prove the assessment web MVP still
  works.
- [ ] Tests do not leave persistent repo data changes.
- [ ] The UI is visually usable on desktop and mobile widths.

## Phase 2: Profile Atom Editing

Goal: let users correct profile atoms without losing provenance.

Tasks:

- [ ] Extend the profile atom review contract with editable fields.
  - Add or document `original_claim`, edited `claim`, `user_note`, and
    `review_history`.
  - Preserve generated text as provenance when a user edits the claim.
- [ ] Extend `review_atom` in the session store.
  - Support claim edits, notes, feedback state, activation scope, and timestamped
    history entries.
- [ ] Add web API support for atom edits.
  - Keep edits session-scoped and atom-id scoped.
  - Return the updated atom after mutation.
- [ ] Add UI controls for editing.
  - Inline edit or compact modal is acceptable.
  - User should be able to confirm, reject, keep review-only, edit claim text,
    and add a note.
- [ ] Add tests for edit persistence and history.
  - Confirm edits survive reload and appear in the aggregate workbench.
- [ ] Update docs.
  - Reflect edit semantics in profile atom output docs, session-storage docs,
    and web MVP docs.

Acceptance criteria:

- [ ] A user can edit an atom claim and still inspect the original generated
  claim.
- [ ] A user note can be stored without changing raw assessment responses.
- [ ] Edited atoms remain non-diagnostic and user-visible.

## Phase 3: Evidence And Uncertainty Views

Goal: make every profile claim inspectable.

Tasks:

- [ ] Add score evidence panels.
  - Show raw score, normalized score, score range, scoring method, and scale id.
- [ ] Add item-level evidence expansion.
  - Show item ids, response values, keying direction, and reverse-scored status.
- [ ] Add instrument/source context.
  - Show instrument name, construct system, license posture, source URL when
    available, and interpretation notes.
- [ ] Add uncertainty/caution text.
  - Explain brief instrument limitations for TIPI.
  - Explain reliability-derived confidence for Mini-IPIP where available.
  - Keep neuroticism/emotional-stability language non-diagnostic.
- [ ] Add evidence view tests.
  - Verify evidence appears for at least TIPI and Mini-IPIP sample sessions.
- [ ] Update docs.
  - Document evidence display requirements and interpretation boundaries.

Acceptance criteria:

- [ ] A user can answer why a score-derived atom exists.
- [ ] A user can see the exact assessment evidence behind a claim.
- [ ] The UI clearly distinguishes self-report evidence from identity facts.

## Phase 4: Scoped Profile Context Export

Goal: create the first profile packet that future generation flows can consume.

Tasks:

- [ ] Define a profile context packet schema.
  - Include selected active/contextual atoms, confidence, evidence summaries,
    contraindications, and generation-safe language.
- [ ] Add a session-store or profile-store helper to build the packet.
  - Default to confirmed/contextual atoms.
  - Exclude suppressed atoms.
  - Include review-only atoms only when explicitly requested.
- [ ] Add a web API route for profile context export.
- [ ] Add UI controls in the workbench.
  - Export confirmed/contextual profile context.
  - Optionally include provisional atoms for internal testing.
- [ ] Add tests for export filtering.
- [ ] Update docs.
  - Document what the packet can and cannot be used for.

Acceptance criteria:

- [ ] The repo can produce a scoped profile context JSON packet.
- [ ] Suppressed/rejected atoms are excluded by default.
- [ ] The packet preserves uncertainty and source provenance.

## Phase 5: First Generation Pilot

Goal: close the first assess -> inspect -> correct -> use loop.

Tasks:

- [ ] Choose one low-risk generation artifact.
  - Recommended first artifact: writing voice guide or communication style
    summary.
- [ ] Add a local generation prompt template.
  - Input should be the scoped profile context packet.
  - Output should avoid diagnosis, protected traits, and fixed identity claims.
- [ ] Add a local dry-run mode.
  - Render the prompt and context without calling any external model.
- [ ] Add a model-backed mode later only after the prompt contract is reviewed.
- [ ] Add feedback capture.
  - Store whether output feels accurate, useful, too strong, too generic, or
    wrong.
- [ ] Feed user feedback back into atom confidence or mapping notes.
- [ ] Update docs.
  - Document pilot scope, risks, and evaluation criteria.

Acceptance criteria:

- [ ] A confirmed profile context packet can produce a first user-visible
  writing/communication artifact.
- [ ] The user can evaluate and correct the output.
- [ ] Generation does not treat assessment scores as deterministic personality
  truth.

## Current Priority

Start with Phase 1. The next code commit should add tests and browser QA before
the atom editing feature expands the behavioral surface.
