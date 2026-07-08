# AGENTS.md

Instructions for AI coding agents working in this repository.

## Repo posture

- This repo is research-first and safety-conscious.
- Do not frame the system as a true personality detector, mind reader,
  diagnostic engine, or literal neuroscience engram.
- Prefer evidence-backed, user-correctable, non-diagnostic language.

## Core workflow

Before substantial work, read:

- `docs/project-memory.md`
- `docs/current-state.md`

When research changes implementation, follow:

- `docs/architecture/rag/research-promotion-workflow.md`

When profile-atom behavior changes, follow:

- `kb/model/profile_atom_schema_v0.md`
- `docs/adr/2026-07-08-profile-atom-lifecycle.md`

## Research and import rules

- Do not treat metadata imports in `kb/paper_imports/` as reviewed knowledge.
- Prefer precision over throughput for paper imports.
- Use manual metadata for books, ambiguous title matches, and non-Crossref
  records.
- Wikipedia imports must remain slow and serialized.

## Assessment rules

- Assessment results are self-report evidence, not identity facts.
- Assessment-derived atoms should start as `provisional_atom`.
- Default assessment activation scope is `review_only`.
- Broad trait claims should not become global generation controls without
  repeated evidence or user confirmation.

Assessment implementation references:

- `docs/architecture/assessments/profile-atom-output.md`
- `docs/architecture/assessments/session-storage.md`
- `tools/assessment_to_profile_atoms.py`
- `tools/assessment_session_store.py`

## Key directories

- `assessments/` - administrable instrument data and assessment tooling inputs
- `kb/` - reviewed knowledge, source cards, and model docs
- `jsondb/` - local queue and MVP persistence files
- `docs/adr/` - architecture decisions
- `.codex/skills/` - local reusable workflow skills
