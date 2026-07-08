# AGENTS.md

Instructions for agents working under `kb/`.

## Purpose

`kb/` holds reviewed knowledge, source cards, model implications, and research
structures. It is not just a dump of imported citations.

## Promotion rule

Do not jump from imported paper metadata to model claims.

Preferred progression:

1. metadata import in `kb/paper_imports/`
2. reviewed synthesis card in `kb/cards/`
3. ontology or signal-matrix update in `kb/model/`
4. ADR or memory update if architecture changes

## Modeling rules

- Separate observed evidence, candidate atoms, active atoms, and suppressed
  atoms.
- Prefer context-tagged if-then patterns over global essence claims.
- Treat neuroscience and clinical sources as architecture or boundary-setting
  inputs unless the repo explicitly needs something stronger.
- Keep user agency, uncertainty, provenance, and counterevidence visible in the
  model.

## References

- `docs/architecture/rag/research-promotion-workflow.md`
- `kb/model/knowledge_model_v0.md`
- `kb/model/signal_matrix_v0.md`
- `kb/model/profile_atom_schema_v0.md`
- `docs/adr/2026-07-08-profile-atom-lifecycle.md`
