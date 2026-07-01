# RAG Structure

## Purpose

The internal RAG is the research memory for the personality and style modeling
platform. It stores curated knowledge, source metadata, model implications, and
planning context so future work can retrieve evidence before making product,
architecture, or inference decisions.

The RAG should answer questions like:

- What evidence supports this personality/style construct?
- What data source can responsibly support this inference?
- What are the limits or cautions around this claim?
- Which sources should be cited before updating the profile model?
- Which inferences are blocked or high-sensitivity?

## Source of Truth

The source of truth is human-readable Markdown and JSON:

- `kb/00_intent.md` - project intent and boundaries
- `kb/model/knowledge_model_v0.md` - current research ontology
- `kb/model/signal_matrix_v0.md` - data-source to inference-permission map
- `kb/research/research_plan.md` - research expansion workflow
- `kb/research/source_backlog.md` - source backlog by domain
- `kb/cards/*.md` - source cards
- `kb/wiki_imports/*.md` - imported Wikipedia summary cards
- `sources/*.json` - structured source registries
- `jsondb/*.json` - import queue, term inventory, and run logs
- `docs/project-memory.md` - compact future-session context
- `plans/*.md` - product and platform planning skeleton

## Generated Index

The retriever writes a generated index to:

```text
rag_index/index.json
```

The generated index is not the source of truth and is ignored by Git. Rebuild it
from the Markdown/JSON corpus:

```bash
python3 tools/rag.py index
```

## Retrieval Tool

The local retrieval CLI is:

```text
tools/rag.py
```

Common commands:

```bash
python3 tools/rag.py search "construct validity profile evidence"
python3 tools/rag.py context "if then signatures personality context" --top-k 6
```

The first implementation uses dependency-free lexical BM25-style ranking. This
keeps the project inspectable and portable while the ontology is still forming.

## Knowledge Unit Types

### Source Registry Entry

Stored in `sources/sources.json`.

Use for bibliographic metadata:

- `id`
- `title`
- `authors`
- `year`
- `type`
- `url`
- `doi`
- `domains`
- `status`
- `evidence_grade`

### Source Card

Stored in `kb/cards/`.

Use for project-relevant interpretation:

- citation
- source registry id
- domain
- key contribution
- model implications
- limits and cautions
- evidence grade
- useful search terms

### Model Note

Stored in `kb/model/`.

Use for evolving ontology and schema decisions:

- construct categories
- profile atom requirements
- signal permission rules
- blocked and high-sensitivity inferences
- generation mapping hypotheses

### Plan Note

Stored in `plans/`.

Use for product and platform planning:

- product vision
- first wedge
- data and consent
- architecture
- evaluation and safety

## Update Workflow

1. Search the existing RAG before adding new claims.
2. Add or update the source registry entry.
3. Create or update the source card.
4. Update model or plan docs only when the source changes project direction.
5. Rebuild the index.
6. Run at least one search query that should retrieve the new material.

## Retrieval Quality Checks

Use representative queries after updates:

```bash
python3 tools/rag.py search "writing samples permissible inference blocked"
python3 tools/rag.py search "broad traits facets generation controls"
python3 tools/rag.py search "diagnosis abnormal psychology boundary"
```

Good results should surface explanatory sections, not only metadata headers.

## Future Architecture

Add later when the corpus stabilizes:

- paper ingestion helpers for HTML and PDFs
- source-card schema validation
- citation-aware synthesis
- query evaluation set
- hybrid lexical plus embedding retrieval
- local or hosted vector store
- source-level permissions and sensitivity tags
