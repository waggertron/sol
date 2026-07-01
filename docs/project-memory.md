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
- `sources/sources.json` tracks source metadata.
- `tools/rag.py` provides local lexical retrieval.

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

