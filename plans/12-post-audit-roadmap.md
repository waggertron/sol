# Post-Audit Product Roadmap

## Purpose

Track the work that remains after the 2026-07-12 initial-plan audit and
assessment-integrity repair pass.

The full evidence and resolved findings are in:

- `docs/audits/2026-07-12-initial-plan-progress-audit.md`

## Completed Audit Repairs

- [x] Correct item-count confidence fallback behavior.
- [x] Validate assessment response IDs and scale values.
- [x] Prevent reviewed atoms from being overwritten by rescoring.
- [x] Serialize local JSONDB mutations and use atomic replacement.
- [x] Persist consent and exact instrument/scoring provenance for new sessions.
- [x] Enforce atom lifecycle invariants.
- [x] Support selective response/atom deletion and feedback cleanup.
- [x] Refresh operational corpus counts and stale plan directions.

## Remaining Audit Work

### A. Finish The Safe Generation Contract

- [ ] Add user-reviewed, contextual generation-guidance authoring.
- [ ] Persist pilot-run records with prompt version, exact atom references,
  context hash, timestamps, mode, and output metadata.
- [ ] Require feedback to reference a known pilot run and only atoms used in it.
- [ ] Add output structure and safety validation.
- [ ] Repeat the model-backed gate review; dry-run remains the default.

### B. Operationalize Evaluation

- [ ] Define local events for “feels like me,” usefulness, correction, and
  generic-versus-personalized preference.
- [ ] Add a generic baseline comparison to the writing-guide pilot.
- [ ] Report correction, rejection, completion, and feedback distributions.
- [ ] Write a small consenting-user evaluation protocol.

### C. Return To The Original Creative Style Kit Wedge

- [ ] Add explicit consent and provenance for writing-sample ingestion.
- [ ] Extract localized communication/style observations rather than identity
  claims.
- [ ] Add liked/disliked examples and direct style calibration.
- [ ] Produce one writing guide and one short text artifact.
- [ ] Add visual references only after the text feedback loop is validated.

### D. Research And Assessment Work

- [x] Develop the original Sol OCEAN assessment only as an experimental,
  validation-gated candidate; repository design work is complete and tracked in
  `plans/13-sol-ocean-experimental-assessment.md`.
- [ ] Complete independent expert/cognitive review before any pilot or
  activation consideration.
- [ ] Continue paper-tail curation only in high-signal manual clusters.
- [ ] Add retrieval-quality evaluation before expanding the RAG architecture.

### E. Platform Work Deferred Until The Wedge Works

- [ ] Replace JSONDB only when multi-user or multi-process requirements are
  concrete.
- [ ] Add authentication, authorization, migrations, and deployment controls
  as part of that application boundary.
- [ ] Extract reusable consent/profile/generation services after the first
  wedge demonstrates value.

## Current Priority Order

1. Follow `plans/14-personal-creative-style-kit-roadmap.md` for the active
   product sequence.
2. Build generation-guidance authoring, persisted pilot provenance, and the
   local/mock provider contract.
3. Add consented writing evidence, direct style calibration, and operational
   evaluation.
4. Pursue expert/cognitive review of the experimental Sol OCEAN candidate as a
   parallel, non-critical validation track.
5. Keep model-backed and multimodal work behind their explicit gates.
