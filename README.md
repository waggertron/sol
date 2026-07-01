# Sol

Sol is an early research and planning workspace for a user-consented
personality and style modeling platform. The project is investigating whether
personal data, user declarations, and user corrections can support a structured,
evidence-weighted model that helps generative systems produce outputs that feel
more aligned with a user's communication style, creative taste, motivations,
values, and context.

The project intentionally avoids claiming that it can discover a user's "true"
personality or produce a clinical diagnosis. The working goal is narrower:

> Build a user-inspectable, evidence-weighted, context-aware personality and
> style model from consented data, then use that model to personalize generated
> outputs across modalities.

## Intent

Modern generative systems can write, draw, summarize, synthesize, and act, but
they usually lack a durable model of the specific person they are helping. Sol
starts from the hypothesis that a useful user model should not be a single
personality score. It should be a layered, inspectable structure made from:

- stable trait tendencies
- context-specific states and modes
- communication and linguistic markers
- aesthetic and creative preferences
- motivational patterns
- values and goals
- behavioral regularities
- user-declared self-concepts
- contraindications and uncertainty markers

Every profile claim should carry provenance, confidence, context, recency, and
room for user correction. The system should preserve uncertainty instead of
flattening a person into a fixed label.

## First Product Wedge

The first candidate feature set is a Personal Creative Style Kit.

The wedge takes a small set of user-provided materials, such as writing samples,
liked and disliked examples, short calibration answers, and optional moodboard
references. It converts those inputs into editable profile atoms, then uses the
profile to generate artifacts the user can evaluate.

Initial outputs may include:

- communication style summary
- writing voice guide
- aesthetic preference summary
- motivational and value hypotheses
- creative pattern observations
- short bio or positioning statement
- content ideas
- image prompt directions
- visual moodboard description

The main product loop is:

1. The user authorizes or uploads data.
2. The system extracts evidence-backed observations.
3. Observations update profile atoms with confidence and provenance.
4. The user confirms, edits, or rejects profile atoms.
5. Generation uses scoped profile atoms for a specific task.
6. Feedback updates confidence, mappings, and future generation behavior.

## Current State

The repository is currently research-first and assessment-ready. It has:

- a local Markdown/JSON RAG corpus with source cards, planning docs, imported
  Wikipedia summaries, source registries, and import queues
- a JSONDB import queue for pending papers, Wikipedia linked articles, and
  reviewed/rejected imports
- an OCEAN assessment repository with 11 permissive/open instruments, 186
  scales, and 1,539 stored items

The next build target is an MVP assessment web app that can administer one
stored OCEAN instrument, persist responses, compute scores, present results,
and create editable profile atom candidates.

See `docs/current-state.md` for the latest snapshot.

## Future Feature Set

The long-term platform should generalize beyond the first creative wedge while
keeping consent, interpretability, and user control as core primitives.

Candidate product capabilities:

- Profile workbench for viewing, editing, deleting, exporting, and versioning
  profile atoms.
- Consent and source controls for deciding which data can be used for which
  modeling or generation purposes.
- Evidence browser showing why a profile claim exists and which sources support
  or contradict it.
- Multimodal generation adapters for text, image, audio, video, avatar, UI, and
  agent behavior.
- Style transfer and voice continuity tools for writing, brand, creative
  direction, and personal expression.
- Reflective self-modeling flows where users compare system hypotheses against
  their declared self-concept.
- Feedback loops for "feels like me", usefulness, confidence calibration, and
  direct corrections.
- API layer for requesting scoped, permissioned profile context inside other
  applications.
- Evaluation harnesses for construct validity, prediction quality, user
  satisfaction, bias, privacy, and misuse risk.
- Safety controls for sensitive attributes, contraindications, uncertainty
  markers, deletion, audit, and non-diagnostic boundaries.

Candidate platform services:

- data ingestion and source normalization
- consent and permissions
- feature extraction
- profile atom store
- inference engine
- user correction interface
- generation orchestrator
- modality adapters
- feedback loop
- audit, deletion, and export

## Research Foundation

This repository currently prioritizes the knowledge base, assessment corpus,
and architecture plan before application code. The research program pulls from
personality psychology, psychometrics, behavioral science, abnormal psychology,
computational linguistics, aesthetic preference research, motivation and values
research, human-computer interaction, privacy, and model evaluation.

The RAG corpus is intended to help answer questions such as:

- Which constructs are well-supported enough to model?
- Which signals are weak, context-bound, biased, or overclaimed?
- How should user corrections update confidence?
- Which inferences should be forbidden, gated, or marked uncertain?
- What evidence is required before a profile atom can affect generation?

## Non-Goals

Sol is not intended to:

- diagnose mental health conditions
- infer protected traits without explicit user intent and controls
- rank people for employment, housing, lending, insurance, education, legal, or
  similar eligibility decisions
- hide profiling from users
- claim complete psychological accuracy
- present generated personality claims as immutable facts

## Structure

- `kb/00_intent.md` - project intent, boundaries, and operating assumptions.
- `kb/model/knowledge_model_v0.md` - first draft of the expandable knowledge model.
- `kb/research/research_plan.md` - outward-expanding research plan.
- `kb/assessments/` - assessment catalogs and profile atom mapping notes.
- `kb/cards/` - source cards and research notes.
- `kb/paper_imports/` - metadata-only paper imports from queued DOI references.
- `assessments/` - acquired assessment instruments and scoring metadata.
- `docs/current-state.md` - current repo snapshot, counts, and next build target.
- `docs/architecture/rag/structure.md` - RAG architecture and update workflow.
- `docs/architecture/assessments/ocean.md` - OCEAN assessment architecture.
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
python3 tools/rag.py search "TIPI scoring reverse scored items"
python3 tools/rag.py search "paper metadata import personality architecture"
```

Print larger context blocks for downstream prompting:

```bash
python3 tools/rag.py context "construct validity personality profile" --top-k 6
```

The first retriever is lexical BM25-style search so the knowledge base works
without external dependencies or API keys. An embedding-backed retriever can be
added once the source corpus stabilizes.
