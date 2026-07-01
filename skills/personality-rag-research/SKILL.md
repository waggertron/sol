---
name: personality-rag-research
description: Research, expand, and maintain the project-local personality/style-model RAG knowledge base. Use when Codex is asked to add academic sources, create or update source cards, refine the personality engram knowledge model, evaluate permissible inferences from user data, update project plans, or preserve ethical boundaries for personality, behavior, linguistics, abnormal psychology, psychometrics, aesthetics, and multimodal generation research.
---

# Personality RAG Research

## Overview

Use this skill to grow the internal research base for the personality and style
modeling platform. Keep the work evidence-backed, source-attributed,
context-aware, and conservative about psychological claims.

## Workflow

1. Read the current project memory in `docs/project-memory.md`.
2. Search the local RAG before adding new claims:

```bash
python3 tools/rag.py search "<question>"
python3 tools/rag.py context "<question>" --top-k 6
```

3. For new sources, add or update `sources/sources.json`.
4. Create a source card in `kb/cards/` using the standard structure in
   `references/source-card-standards.md`.
5. Update model docs only when the source changes the ontology, signal matrix,
   plans, or safety boundaries.
6. Rebuild and spot-check the index:

```bash
python3 tools/rag.py index
python3 tools/rag.py search "<new source concept>"
```

## Modeling Rules

- Treat "engram" as an internal metaphor, not a literal neuroscience claim.
- Separate observed evidence, style preference, trait hypothesis, and sensitive
  hypothesis.
- Prefer context-tagged if-then patterns over global personality labels.
- Treat broad traits as organizing constructs, not direct generation controls.
- Use abnormal psychology and clinical frameworks mainly for boundary-setting.
- Preserve uncertainty, counterevidence, provenance, and user confirmation.
- Avoid clinical diagnosis, protected-class inference, eligibility decisions,
  covert persuasion, and hidden profiling.

## Source Priority

Prefer primary and rigorous sources:

- peer-reviewed papers
- meta-analyses and major reviews
- established measurement frameworks
- official clinical/research frameworks for boundary design
- reputable methodology references

When using web research, prefer primary sources or official documentation. Record
URLs, DOI values when available, evidence grade, and limits.

## Key Files

- `docs/project-memory.md` - compact project context
- `plans/` - product and platform planning skeleton
- `kb/00_intent.md` - intent and boundaries
- `kb/model/knowledge_model_v0.md` - research ontology
- `kb/model/signal_matrix_v0.md` - permissible inference map
- `kb/cards/` - source cards
- `sources/sources.json` - source registry
- `tools/rag.py` - local retrieval CLI

Read `references/source-card-standards.md` when adding or revising source cards.
