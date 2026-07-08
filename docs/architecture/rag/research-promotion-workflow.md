# Research Promotion Workflow

This document captures the working process used in this repository to turn a
source request into durable knowledge-base structure that can later support
product implementation.

## Purpose

Use this workflow when a source or source cluster should become more than a
queued import candidate.

Target outputs:

- bibliographic metadata cards in `kb/paper_imports/`
- reviewed synthesis cards in `kb/cards/`
- ontology or model updates in `kb/model/`
- architectural decisions in `docs/adr/` when the source changes system design
- memory updates in `docs/project-memory.md` and `docs/current-state.md`

## Working Principle

Do not jump from "paper exists" to "paper controls the model."

The repository uses a staged promotion path:

1. acquire bibliographic metadata
2. cluster related sources
3. write reviewed synthesis cards
4. update ontology and inference boundaries
5. formalize architectural consequences when needed

## Workflow

### 1. Resolve the Requested Source

Determine whether the requested item is:

- a journal article with a DOI
- a chapter or proceedings item with a DOI
- a book or monograph without a clean Crossref work DOI
- a non-Crossref source that needs manual metadata

Preferred resolution order:

1. direct DOI
2. Crossref title lookup
3. manual bibliographic lookup

If the source is a book or nonstandard object, create a manual metadata card
rather than forcing a weak automated match.

## 2. Import Metadata Into the KB

Create or update queue records in:

- `jsondb/import_queue.json`
- `jsondb/paper_import_review.json`

Import outputs go to:

- `kb/paper_imports/`

Relevant commands:

```bash
python3 tools/kb_importer.py import-paper-manual-matches --sleep 0
python3 tools/kb_importer.py import-paper-metadata --limit <n>
```

Use manual matches for curated clusters. Do not run broad title-search batches
when the false-match risk is high.

## 3. Expand to Immediate Related Sources

After importing the primary source, import only the next high-signal ring of
related works.

Preferred related-source criteria:

- direct follow-up works by the same author
- foundational companion papers cited repeatedly in the cluster
- major empirical or theoretical contrast papers
- high-citation items that are structurally central to the cluster

Avoid broad uncontrolled expansion at this stage.

## 4. Write Reviewed Source Cards

Metadata cards are not enough. Promote the cluster into reviewed knowledge by
writing synthesis cards in `kb/cards/`.

Each reviewed card should include:

- citation block
- domain
- key contribution
- model implications
- limits and cautions
- evidence grade
- useful search terms

The reviewed card is the place where the repo decides what the source is for.

## 5. Update the Ontology

If the reviewed source affects the model, update:

- `kb/model/knowledge_model_v0.md`
- `kb/model/signal_matrix_v0.md`

Typical changes:

- add or refine constructs
- tighten inference boundaries
- add lifecycle distinctions
- add activation or threshold rules

This is where source review becomes operational.

## 6. Create an ADR When the Source Changes Architecture

Create an ADR in `docs/adr/` when the source cluster changes:

- storage contracts
- lifecycle rules
- activation or promotion policy
- service boundaries
- product safety architecture

Examples from this repo:

- `docs/adr/2026-07-08-profile-atom-lifecycle.md`
- `docs/adr/2026-07-01-jsondb-import-queue.md`

## 7. Distill Into Project Memory

When a workflow or source cluster becomes important enough to reuse, record it
in:

- `docs/project-memory.md`
- `docs/current-state.md`

Use memory updates for:

- ongoing operating posture
- stable counts or corpus shape
- boundary rules
- important new reviewed source clusters

## 8. Distill Into a Skill When Repetition Appears

Create or update a local skill when the workflow becomes repeatable enough that
future sessions should trigger it automatically.

Good candidates:

- paper-cluster ingestion and promotion
- assessment acquisition and normalization
- slow queue-drain import discipline

Skill location for this repo:

- `.codex/skills/`

## Decision Heuristics

### Use Manual Metadata When

- the source is a book
- Crossref has no direct work record
- the DOI resolves to a non-Crossref object
- title search is ambiguous

### Write a Reviewed Card When

- the source changes how the model should behave
- multiple imported metadata cards belong to one conceptual cluster
- the repo needs a reusable interpretation rather than raw citation storage

### Update the Model When

- the source implies a new lifecycle or inference boundary
- the source changes what can become a generation control
- the source changes how evidence should be aggregated or suppressed

## Current Example Cluster

The Bernard Baars / global-workspace cluster followed this workflow:

1. import the 1988 Baars book as manual metadata
2. import closely related workspace and conscious-access papers
3. write reviewed cards:
   - `kb/cards/baars_global_workspace_theory.md`
   - `kb/cards/dehaene_workspace_neuroscience.md`
4. update:
   - `kb/model/knowledge_model_v0.md`
   - `kb/model/signal_matrix_v0.md`
5. formalize:
   - `docs/adr/2026-07-08-profile-atom-lifecycle.md`
   - `kb/model/profile_atom_schema_v0.md`

## Anti-Patterns

Avoid:

- importing weak title matches just to increase counts
- treating metadata cards as reviewed knowledge
- converting neuroscience or clinical language into product claims
- promoting broad trait claims directly into global generation control
- skipping memory and ADR updates when a source changes implementation posture
