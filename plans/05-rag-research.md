# RAG Research Plan

## Objective

Build an internal knowledge base that helps evaluate the scientific and product
feasibility of personality/style modeling.

## Current Implementation

- Markdown source cards in `kb/cards/`
- source registry in `sources/sources.json`
- adjacent source registry in `sources/adjacent_sources_v1.json`
- ontology drafts in `kb/model/`
- assessment notes in `kb/assessments/`
- metadata-only paper imports in `kb/paper_imports/`
- acquired OCEAN instruments in `assessments/ocean/`
- JSONDB import queue in `jsondb/import_queue.json`
- local lexical retriever in `tools/rag.py`

Current snapshot:

- 2,275 RAG chunks
- 123 Wikipedia summary cards
- 25 paper metadata cards
- 3,373 import queue entries
- 11 OCEAN assessment instruments

See `docs/current-state.md` for details.

## Expansion Workflow

1. Add source to `sources/sources.json`.
2. Read the source and create a source card.
3. Extract model implications and cautions.
4. Update the source backlog or knowledge model.
5. Rebuild the local index.
6. Query the index against project-critical questions.

For assessment imports, use the separate assessment workflow documented in
`docs/architecture/assessments/ocean.md`.

## Evidence Grades

- `A`: foundational, major review, meta-analysis, or established construct
- `B`: peer-reviewed empirical paper
- `C`: credible framework or professional documentation
- `D`: speculative or internal hypothesis

## Next Research Domains

- psychometrics and validity
- language/personality inference
- digital footprint privacy
- aesthetic preference and creativity
- consent UX and explainable personalization
