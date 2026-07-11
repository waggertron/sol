# Scoped Profile Context Packet

## Purpose

Provide a generation-facing export of user-reviewed profile context without
exposing the whole assessment session or treating provisional claims as active
instructions.

## Default Selection

An atom is included by default only when:

- `state` is `active_atom`
- `activation_scope` is `contextual` or `global`
- `user_feedback` is `confirmed` or `edited`
- `sensitivity_level` is not `blocked`

`suppressed_atom` records are always excluded.

When `include_review_only` is explicitly enabled, non-rejected
`observed_candidate` and `provisional_atom` records with `review_only` scope are
also included. They are marked `eligible_for_generation: false` and are for
internal inspection, not steering.

## Shape

The packet contains:

- `schema_version`
- `generated_at`
- `selection_policy`
- `safety`
- `atom_count`
- `atoms`

Each selected atom contains:

- stable id, label, domain, and user-visible claim
- lifecycle state, activation scope, and generation eligibility
- context and confidence
- evidence summaries and source ids
- contraindications from counterevidence
- generation guidance
- generation-guidance notes linked to prior feedback events
- uncertainty including stability, recency, sensitivity, and assessment caution
- user feedback and last-updated timestamp

## Commands And API

```bash
python3 tools/assessment_session_store.py export-profile-context \
  --generated-at 2026-07-11T00:00:00Z
```

Web exports:

- `GET /api/profile-context`
- `GET /api/profile-context?include_review_only=true`

## Boundaries

- This is not a session backup; raw responses and item text are omitted.
- Review-only records are never marked generation-eligible.
- The packet must not be used for diagnosis, protected-class inference, hidden
  profiling, or eligibility/high-impact decisions.
- Consumers should apply contextual atoms only when their context matches the
  generation task.
