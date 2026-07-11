# 2026-07-11: Scoped Profile Context Packet

## Problem Statement

The assessment MVP can now produce, explain, and correct profile atoms. Future
generation experiments need a stable handoff format, but exporting every stored
atom as a steering instruction would collapse the distinction between
provisional evidence and generation-eligible profile context.

The packet must preserve provenance and uncertainty, exclude rejected or
suppressed claims, and make any internal inclusion of review-only candidates
explicit and non-generative.

## Options Evaluated

### Option A: Export All Stored Atoms

| Pros | Cons |
|------|------|
| Simplest implementation | Weak or rejected claims can steer generation |
| Complete storage snapshot | Consumers must reproduce lifecycle policy |

### Option B: Export Only Active Scoped Atoms With An Explicit Review Override

| Pros | Cons |
|------|------|
| Safe default for generation | Packet is not a complete storage backup |
| Central filtering policy | Requires a separate internal-testing flag |
| Preserves provenance and uncertainty | Adds a dedicated schema |

### Option C: Let Each Generator Query Session Storage Directly

| Pros | Cons |
|------|------|
| No intermediate format | Couples generators to JSONDB and lifecycle details |
| Flexible per experiment | Filtering can drift across consumers |

## Decision

Choose Option B. The default packet contains only `active_atom` records with
`contextual` or `global` activation scope, `confirmed` or `edited` user
feedback, and non-blocked sensitivity. Rejected and suppressed atoms remain
excluded. An explicit `include_review_only` option may add provisional review
candidates for internal inspection, but those records carry
`eligible_for_generation: false`.

The packet is personalization context, not a personality diagnosis or identity
record. It carries prohibited-use guidance alongside the selected atoms.

## Implementation Details

- Define the packet contract in
  `docs/architecture/assessments/profile-context-packet.md`.
- Build packets through `build_profile_context` in
  `tools/assessment_session_store.py` so CLI and web callers share filtering.
- Expose `GET /api/profile-context` with an optional
  `include_review_only=true` query parameter.
- Preserve claims, context, confidence, evidence summaries, source ids,
  counterevidence, uncertainty, and generation guidance.
- Exclude rejected and suppressed atoms in every mode.
