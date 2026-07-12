---
name: sol-experimental-assessment-workflow
description: Use when designing, reviewing, revising, validating, or considering activation of a project-authored Sol assessment candidate; when editing experimental assessment JSON, construct blueprints, item pools, scoring drafts, manifest status, collision checks, or pilot gates; or when deciding whether an original assessment is ready for expert review, cognitive interviews, empirical piloting, or product administration.
---

# Sol Experimental Assessment Workflow

Build original assessment candidates as validation-gated design artifacts. Keep
repository completeness separate from psychometric evidence and product
activation.

## Read First

Read completely:

- `AGENTS.md`
- `assessments/AGENTS.md`
- `docs/project-memory.md`
- `docs/current-state.md`
- `plans/13-sol-ocean-experimental-assessment.md`
- `docs/architecture/assessments/sol-ocean-experimental.md`

For Sol OCEAN work, also read:

- `kb/assessments/sol_ocean_construct_blueprint_v0.md`
- `kb/cards/big_five_trait_structure.md`
- `kb/cards/construct_validity_psychometrics.md`
- `kb/cards/caps_person_situation.md`
- `kb/cards/whole_trait_theory.md`

## Workflow

1. **Check the evidence layer.** Use reviewed cards and model docs for construct
   claims. Do not promote metadata-only paper imports into item or scoring
   decisions.
2. **Update the blueprint before the item pool.** Define inclusion, exclusion,
   related constructs, failure modes, sensitivity, and later validity questions.
3. **Write candidate items under the experimental contract.** Use original
   wording, stable IDs, explicit domain/subconstruct traceability, keying,
   reading target, sensitivity, failure modes, and design provenance.
4. **Keep candidates inactive.** Store them below
   `assessments/<family>/experimental/`, set
   `administration_status: experimental_design_review_only`, disable product
   profile output, and keep them out of administrable manifests.
5. **Validate structure and collision boundaries.** For the current OCEAN
   candidate, run:

   ```bash
   python3 tools/validate_sol_ocean_candidate.py
   ./scripts/run_assessment_web_mvp_qa.sh
   ```

6. **Use deliberate invalid fixtures.** Test malformed keying, missing metadata,
   wording collisions, manifest leakage, and product-flow rejection separately
   from valid candidate data.
7. **Stop at the correct gate.** Repository validation does not establish
   reliability, validity, norms, invariance, or usefulness. Do not activate a
   candidate before independent expert review, cognitive interviews, a named
   pilot ADR, and the empirical work required by the plan.
8. **Distill durable changes.** Update the candidate plan, architecture docs,
   `docs/current-state.md`, and `docs/project-memory.md`. Add an ADR when a pilot
   or activation decision changes the product boundary.

## Non-Negotiable Boundaries

- Do not call a project-authored candidate validated without empirical evidence.
- Do not copy proprietary or permission-unclear item wording.
- Do not use clinical, protected-trait, competence, morality, or eligibility
  content as ordinary personality items.
- Do not turn broad trait scores directly into global generation controls.
- Do not add an experimental form to the web manifest as a convenience shortcut.

## Current Canonical Artifacts

- Blueprint: `kb/assessments/sol_ocean_construct_blueprint_v0.md`
- Candidate: `assessments/ocean/experimental/sol_ocean_quick_v0.json`
- Validator: `tools/validate_sol_ocean_candidate.py`
- Contract: `docs/architecture/assessments/sol-ocean-experimental.md`
- Ledger: `plans/13-sol-ocean-experimental-assessment.md`

