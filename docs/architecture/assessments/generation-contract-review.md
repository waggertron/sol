# Generation Prompt And Feedback Contract Review

Review date: 2026-07-11

## Decision

The model-backed generation gate is **not yet approved**.

The local dry-run and feedback contracts are suitable for continued local
development after the hardening in this review, but enabling an external model
would currently create pressure to invent style rules from broad assessment
claims. Assessment-derived atoms have no user-reviewed generation mappings by
default, and feedback events are not yet constrained to a persisted pilot run.

## Findings Resolved

- Generation eligibility now requires `active_atom`, `contextual` or `global`
  scope, `confirmed` or `edited` user feedback, and non-blocked sensitivity.
- Context selection and feedback validation share the same eligibility rule.
- User-edited claims are serialized as JSON user data, separate from the system
  instruction; the system instruction says embedded commands are data, not
  instructions.
- Every dry run has an explicit bounded `pilot_id` and prompt-contract version.
- Negative feedback requires an explanatory note.
- Duplicate atom references, oversized ids/notes, and feedback targeting an
  ineligible atom are rejected.
- Feedback remains append-only and does not silently change assessment
  responses, claims, or confidence.

## Remaining Entry Conditions

Before adding a model-backed mode:

1. Add a user-reviewed authoring path for concrete generation guidance.
   Assessment claims with empty `generation_mappings` should remain questions,
   not be converted into style instructions by a model.
2. Persist pilot-run records with pilot id, prompt-contract version, exact atom
   references, timestamps, and eventual output metadata. Feedback must target a
   known run and only atoms actually used by that run.
3. Define the provider boundary and explicit user opt-in. The default command
   must remain dry-run and must not require cloud credentials.
4. Add output validation for required sections, prohibited diagnostic or fixed-
   identity framing, and provenance back to the pilot run.
5. Add an end-to-end test proving rejected, suppressed, unconfirmed, blocked,
   and review-only atoms cannot reach a model request.

## Review Evidence

- Automated tests cover confirmed selection, unconfirmed active exclusion,
  blocked-sensitivity exclusion, prompt-injection separation, negative-feedback
  notes, duplicate references, invalid values, and raw-response preservation.
- The repository QA command passes with tracked assessment storage unchanged.

## Progress Since Review

- `tools/style_kit_guidance.py` now provides the domain-level user review path
  for proposed, confirmed, edited, and disabled guidance.
- Guidance activation uses the same shared profile-atom eligibility policy as
  scoped assessment context export and never derives an instruction from a
  broad assessment claim automatically.
- A browser/API authoring surface is still open.
- `tools/style_kit_pilot.py` now persists exact generic/personalized dry-run and
  mock records with versioned prompt-safe guidance snapshots, request/context
  hashes, and bounded output validation.
- External-provider opt-in, evaluation binding, the full exclusion test at the
  eventual provider request boundary, and browser/API surfaces remain open, so
  model-backed mode is still not approved.
