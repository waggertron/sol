# Assessment Session Storage

This document defines the first local persistence layer for the
assessment-first MVP.

## Purpose

Store:

- session metadata
- raw responses
- derived scores
- derived provisional profile atoms
- item-level scoring evidence and instrument context needed to explain derived
  results

This is a local JSONDB persistence layer intended for early implementation and
testing before a multi-user application database exists.

## Storage File

- `jsondb/assessment_sessions.json`

## Session Shape

Each session stores:

- `session_id`
- `user_id`
- `instrument_id`
- `instrument_name`
- `instrument_path`
- `status`
- `started_at`
- `completed_at`
- `responses`
- `scores`
- `profile_atoms`

`responses` are stored separately from `scores` so scoring can be regenerated.

## Tool

Use:

- `tools/assessment_session_store.py`

For tests and local QA, set `SOL_ASSESSMENT_SESSIONS_DB` to point the session
store at an isolated JSON file. If unset, the default path remains
`jsondb/assessment_sessions.json`.

Supported commands:

```bash
python3 tools/assessment_session_store.py init-db
python3 tools/assessment_session_store.py create-session --session-id session_001 --instrument assessments/ocean/instruments/tipi.json --started-at 2026-07-08T21:00:00Z
python3 tools/assessment_session_store.py save-responses --session-id session_001 --responses assessments/ocean/examples/tipi_sample_responses.json
python3 tools/assessment_session_store.py score-session --session-id session_001 --completed-at 2026-07-08T21:05:00Z
python3 tools/assessment_session_store.py list-sessions
python3 tools/assessment_session_store.py list-profile-atoms
python3 tools/assessment_session_store.py export-profile-context --generated-at 2026-07-11T00:00:00Z
python3 tools/assessment_session_store.py record-generation-feedback --event-id feedback_001 --pilot-id writing_guide_001 --recorded-at 2026-07-11T00:05:00Z --feedback useful --atom-ref 'session_001::assessment.tipi.tipi_extraversion.v0'
python3 tools/assessment_session_store.py show-session --session-id session_001
python3 tools/assessment_session_store.py review-atom --session-id session_001 --atom-id assessment.tipi.tipi_extraversion.v0 --reviewed-at 2026-07-08T21:10:00Z --user-feedback confirmed --state active_atom --activation-scope contextual
python3 tools/assessment_session_store.py review-atom --session-id session_001 --atom-id assessment.tipi.tipi_extraversion.v0 --reviewed-at 2026-07-08T21:12:00Z --user-feedback edited --claim "I often enjoy social interaction in familiar settings." --user-note "Large groups are different."
python3 tools/assessment_session_store.py delete-session --session-id session_001
```

## Policy

- raw responses remain stored
- scores are derived and reproducible
- score records preserve response-to-keyed-value calculation details; profile
  atoms retain a copy of the relevant explanation metadata for aggregate views
- profile atoms generated from assessment scoring start as
  `provisional_atom` and `review_only`
- future app code should not bypass the lifecycle contract in
  `kb/model/profile_atom_schema_v0.md`
- user review should flow through explicit atom updates rather than silently
  mutating raw scores
- the first edit preserves generated wording in `original_claim`; later edits
  update only `claim`
- material claim, note, feedback, state, and scope changes append timestamped
  field-level entries to `review_history`
- older stored atoms gain the edit-provenance fields lazily on first review
- deletion removes a whole local session, including responses, derived scores,
  and derived profile atoms
- scoped context export includes only active contextual/global atoms by default;
  rejected and suppressed atoms are always excluded
- pilot feedback is stored separately at the JSONDB root and linked to scoped
  atoms through append-only generation mapping notes and source ids

## Near-Term Role

This layer is sufficient for:

- command-line smoke testing
- fixture generation
- early MVP integration
- later migration into application-backed storage
