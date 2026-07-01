# RAG Research Plan

## Objective

Build an internal knowledge base that helps evaluate the scientific and product
feasibility of personality/style modeling.

## Current Implementation

- Markdown source cards in `kb/cards/`
- source registry in `sources/sources.json`
- ontology drafts in `kb/model/`
- local lexical retriever in `tools/rag.py`

## Expansion Workflow

1. Add source to `sources/sources.json`.
2. Read the source and create a source card.
3. Extract model implications and cautions.
4. Update the source backlog or knowledge model.
5. Rebuild the local index.
6. Query the index against project-critical questions.

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

