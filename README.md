# Personality Engram Knowledge Base

This workspace is an internal research and RAG scaffold for evaluating whether a
user-consented data model can infer stable, useful personality/style signals and
use them to guide multimodal generation.

The project intentionally avoids claiming that it can discover a user's "true"
personality. The working goal is narrower:

> Build a user-inspectable, evidence-weighted, context-aware personality and
> style model from consented data, then use that model to personalize generated
> outputs across modalities.

## Structure

- `kb/00_intent.md` - project intent, boundaries, and operating assumptions.
- `kb/model/knowledge_model_v0.md` - first draft of the expandable knowledge model.
- `kb/research/research_plan.md` - outward-expanding research plan.
- `kb/cards/` - source cards and research notes.
- `docs/architecture/rag/structure.md` - RAG architecture and update workflow.
- `docs/project-memory.md` - compact context for future sessions.
- `plans/` - product and platform planning skeleton.
- `sources/*.json` - source registries for papers, frameworks, and references.
- `jsondb/` - import queue, term inventory, and import run logs.
- `tools/rag.py` - local standard-library retrieval CLI.
- `tools/kb_importer.py` - import queue and Wikipedia/Crossref helper.
- `rag_index/` - generated retrieval index.

## Local RAG

Build the index:

```bash
python3 tools/rag.py index
```

Search the internal knowledge base:

```bash
python3 tools/rag.py search "personality problem solving context traits"
python3 tools/rag.py search "why avoid diagnostic claims"
python3 tools/rag.py search "language cues digital footprints personality"
```

Print larger context blocks for downstream prompting:

```bash
python3 tools/rag.py context "construct validity personality profile" --top-k 6
```

The first retriever is lexical BM25-style search so the knowledge base works
without external dependencies or API keys. An embedding-backed retriever can be
added once the source corpus stabilizes.
