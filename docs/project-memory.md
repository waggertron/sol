# Project Memory

This is the compact context to preserve across future planning and development
sessions.

## Project Intent

Build a platform for user-consented personality and style modeling. The system
should infer evidence-weighted, user-correctable profile atoms from authorized
data, then use those atoms to personalize generated outputs across modalities.

Do not frame the system as a true personality detector, mind reader, diagnostic
engine, or literal neuroscience engram.

Preferred framing:

> an evidence-backed, user-correctable personality and style model for
> personalized multimodal generation

## Initial Product Strategy

The long-term product is a platform, but the first implementation should be a
single wedge that exercises the complete loop.

Current recommended wedge:

> Personal Creative Style Kit

The wedge should ingest user-provided writing samples, preferences, examples,
and direct calibration answers; produce an editable personality/style profile;
then generate text and visual direction the user can evaluate.

## Core Loop

1. User authorizes or provides data.
2. System extracts observations with source provenance.
3. Observations become provisional profile atoms.
4. User confirms, edits, rejects, or scopes those atoms.
5. Generation uses confirmed or high-confidence atoms.
6. Output feedback updates the profile.

## Research Principles

- Use rigorous psychology, psychometrics, linguistics, behavioral science,
  abnormal psychology, HCI, and computational social science.
- Keep observed data, style preference, trait hypothesis, and sensitive
  hypothesis separate.
- Prefer context-aware if-then patterns over global personality labels.
- Treat broad trait models as organizing layers, not direct generation controls.
- Use clinical and abnormal psychology mainly for boundary-setting.
- Store confidence, counterevidence, context, recency, and user confirmation.

## Current Knowledge Base Shape

- `kb/00_intent.md` defines project intent and boundaries.
- `kb/model/knowledge_model_v0.md` defines the first research ontology.
- `kb/model/signal_matrix_v0.md` maps data sources to permissible inference
  levels.
- `kb/cards/` contains source cards.
- `kb/assessments/` contains OCEAN assessment catalog and profile atom mapping
  notes.
- `sources/sources.json` tracks source metadata.
- `sources/adjacent_sources_v1.json` tracks 34 adjacent research sources.
- `jsondb/import_queue.json` tracks 3,373 pending/imported/rejected research
  import candidates.
- `assessments/ocean/` stores the current OCEAN assessment corpus: 11
  instruments, 186 scales, and 1,539 items.
- `tools/rag.py` provides local lexical retrieval.
- `tools/kb_importer.py` manages research import queues.
- `tools/import_ocean_assessments.py` normalizes downloaded official assessment
  pages into repo JSON.

The latest snapshot is maintained in `docs/current-state.md`.

## Current Build Direction

Build the first MVP around assessment administration before broader generation:

1. Load an instrument from `assessments/ocean/manifest.json`.
2. Administer TIPI, Mini-IPIP, or IPIP-NEO-60.
3. Persist responses and scores with assessment-version provenance.
4. Present non-diagnostic results with uncertainty.
5. Let users confirm, edit, reject, export, or delete profile atom candidates.

## Key Source Anchors

- Frontiers 2022 paper that inspired the project: trait-context-behavior-output
  layering.
- Big Five and HEXACO: broad trait structure.
- CAPS and Whole Trait Theory: context, dynamics, if-then signatures, and
  state distributions.
- Cronbach and Meehl: construct validity and nomological networks.
- Schwartz et al. and Youyou et al.: language and digital footprint inference.
- ICD-11, HiTOP, RDoC: clinical boundary awareness, not product diagnosis.

## Hard Boundaries

Default blocked:

- clinical diagnosis
- personality disorder labeling
- protected class inference
- covert political persuasion
- hidden profiling
- employment, housing, lending, insurance, legal, or education eligibility use

Default high-sensitivity:

- trauma interpretations
- maladaptive personality extremes
- honesty/exploitiveness claims
- emotional instability claims
- attachment-style claims
- intelligence or competence claims
