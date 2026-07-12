# Experimental Sol OCEAN Assessment Contract

## Purpose

Define the repository boundary for original Sol OCEAN candidates while they are
being designed and reviewed.

The reusable implementation/review workflow is maintained at:

- `.codex/skills/sol-experimental-assessment-workflow/SKILL.md`

## Current Candidate

- id: `sol_ocean_quick_v0`
- location: `assessments/ocean/experimental/sol_ocean_quick_v0.json`
- status: `experimental_design_review_only`
- item count: 30
- intended coverage: five domains, three candidate subconstructs per domain,
  two items per subconstruct

## Storage And Activation Rules

- Experimental forms live under `assessments/ocean/experimental/`.
- They do not appear in `assessments/ocean/manifest.json`.
- The browser MVP must not list or administer them.
- The scoring engine must not emit product profile atoms from them until a
  later ADR approves a limited pilot.
- Candidate JSON may contain original item wording because it is authored for
  this project, but it must retain design provenance and collision checks.

## Item Contract

Every candidate item includes:

- stable id and source order
- OCEAN domain and candidate subconstruct
- original wording
- positive or negative keying
- blueprint reference
- sensitivity level
- reading target
- expected failure modes
- design provenance

Initial balance requires exactly two items per subconstruct and equal positive /
negative keying within each subconstruct.

## Draft Scoring Contract

The candidate records a draft `sum_keyed_items` specification using a 1-5
accuracy response scale. Negative items would be reverse-keyed before summing.
This scoring metadata exists for structural review and later pilot planning; it
does not create norms, cutoffs, validated interpretations, or product confidence.

## Review Gates

1. Structural validator passes.
2. No exact normalized item-text collision exists with stored instruments.
3. Independent construct and item-writing review is completed.
4. Cognitive interviews identify ambiguous or harmful wording.
5. A named pilot form is frozen through an ADR.
6. Empirical pilot and validation evidence are collected before product use.

## Prohibited Claims

Do not describe the candidate as validated, reliable, normed, diagnostic,
clinically meaningful, culturally invariant, or predictive of eligibility or
real-world performance.
