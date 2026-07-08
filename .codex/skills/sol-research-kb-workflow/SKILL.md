---
name: sol-research-kb-workflow
description: Use when working in this repository on paper ingestion, related-source expansion, reviewed source cards, ontology promotion, profile-atom lifecycle updates, or memory/ADR distillation for the Sol personality-model knowledge base.
---

# Sol Research KB Workflow

Use this skill when a user asks to import a paper, expand a source cluster, or
turn research into durable repository knowledge.

## Core Workflow

1. Resolve the requested source:
   - prefer direct DOI
   - use Crossref title lookup if safe
   - use manual metadata for books, monographs, or ambiguous records
2. Import metadata into:
   - `jsondb/import_queue.json`
   - `jsondb/paper_import_review.json`
   - `kb/paper_imports/`
3. Expand only to the immediate high-signal related cluster.
4. Write reviewed synthesis cards in `kb/cards/`.
5. If the cluster changes model behavior, update:
   - `kb/model/knowledge_model_v0.md`
   - `kb/model/signal_matrix_v0.md`
6. If the cluster changes architecture or contracts, add an ADR in `docs/adr/`.
7. Update:
   - `docs/current-state.md`
   - `docs/project-memory.md`

## Operating Rules

- Do not treat metadata cards as reviewed knowledge.
- Do not force weak Crossref title matches.
- Prefer precision over throughput.
- Use neuroscience or clinical sources only for architecture, boundary-setting,
  or evidence-handling unless the repo explicitly needs something stronger.
- Broad trait claims should not become global active atoms without repeated
  evidence or user confirmation.

## Important Files

- `docs/architecture/rag/research-promotion-workflow.md`
- `kb/model/profile_atom_schema_v0.md`
- `docs/adr/2026-07-08-profile-atom-lifecycle.md`
- `plans/09-paper-tail-curation.md`

## Commands

```bash
python3 tools/kb_importer.py import-paper-manual-matches --sleep 0
python3 tools/kb_importer.py import-paper-metadata --limit <n>
python3 tools/kb_importer.py apply-paper-review
python3 tools/kb_importer.py paper-review-report --limit 200 --output kb/research/paper_review_queue.md
```

## Current Local Posture

- Wikipedia imports must remain slow and serialized.
- The remaining general paper tail is a review queue, not a blind bulk-import
  target.
- High-signal source clusters should be promoted through reviewed cards, model
  docs, and ADRs when warranted.
