# 2026-07-01: Local Markdown and BM25 RAG Scaffold

## Problem Statement

The project needs an internal knowledge base for evaluating whether a
user-consented personality/style model is technically and ethically viable. The
knowledge base must start immediately, remain inspectable, preserve source
provenance, and avoid depending on external services before the research corpus
and ontology stabilize.

Constraints:

- The workspace started empty.
- The initial corpus is curated research notes and source metadata.
- The project needs repeatable retrieval without API keys.
- The system should support future embedding-backed retrieval after the corpus
  matures.

## Options Evaluated

### Option A: Local Markdown/JSON with Dependency-Free BM25

Store source cards and model notes as Markdown/JSON. Build a small lexical
retrieval index with a standard-library Python script.

| Pros | Cons |
|------|------|
| Works immediately without services or keys | Lexical search misses semantic matches |
| Easy to inspect, diff, and review | Ranking quality is basic |
| Keeps source cards human-editable | No built-in citation synthesis |
| Low operational cost | Generated index must be rebuilt |

### Option B: Embedding Database from the Start

Use a vector database or local embedding store as the primary retrieval layer.

| Pros | Cons |
|------|------|
| Better semantic retrieval | Adds model and dependency choices too early |
| More scalable for large corpora | Harder to inspect and diff |
| Useful for downstream RAG product design | Requires embedding refresh workflows |
| Can combine with hybrid retrieval | More moving parts before ontology is stable |

### Option C: Free-Form Notes Only

Keep planning and source notes in ordinary Markdown without retrieval tooling.

| Pros | Cons |
|------|------|
| Fastest possible start | Harder to reuse context reliably |
| No implementation work | Research retrieval becomes manual |
| Fully human-readable | No path toward internal RAG evaluation |

## Decision

Choose Option A: local Markdown/JSON source-of-truth plus a dependency-free
BM25-style retriever.

This gives the project an immediately usable internal RAG while preserving
reviewability. It also keeps the system honest: the first phase is about
building a rigorous knowledge model, not prematurely optimizing retrieval
infrastructure.

Embeddings should be added later as a hybrid layer once the source corpus,
source-card format, and ontology are more stable.

## Implementation Details

Implemented files:

- `kb/00_intent.md`
- `kb/model/knowledge_model_v0.md`
- `kb/model/signal_matrix_v0.md`
- `kb/research/research_plan.md`
- `kb/research/source_backlog.md`
- `kb/cards/*.md`
- `sources/sources.json`
- `tools/rag.py`

Generated output:

- `rag_index/index.json`

The generated index is ignored by Git and can be rebuilt with:

```bash
python3 tools/rag.py index
```

Future follow-up:

- add paper ingestion helpers for PDFs and HTML
- add source-card validation
- add hybrid lexical plus embedding retrieval
- add a query-evaluation set for research questions
- add citation-aware synthesis once source coverage is stronger

