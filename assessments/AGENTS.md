# AGENTS.md

Instructions for agents working under `assessments/`.

## Purpose

This tree stores administrable instrument data, not reviewed research
interpretation.

## Rules

- Store full item text only when the source posture is public-domain,
  explicitly permissive, or otherwise approved.
- Do not copy proprietary, clinical, or permission-unclear item text or norms
  into this tree.
- Keep instrument JSON aligned with the import format already used in
  `assessments/ocean/instruments/`.

## Output behavior

- Scoring output should align with `kb/model/profile_atom_schema_v0.md`.
- Assessment-derived atoms should begin as `provisional_atom` and
  `review_only`.
- Keep raw responses separable from derived scores and derived atoms.

## References

- `docs/architecture/assessments/ocean.md`
- `docs/architecture/assessments/profile-atom-output.md`
- `docs/architecture/assessments/session-storage.md`
- `docs/architecture/assessments/mvp-flow.md`
- `kb/assessments/ocean_profile_atom_mapping_v0.md`
- `.codex/skills/sol-experimental-assessment-workflow/SKILL.md` for original
  project-authored candidate design and activation gates
