# Knowledge Model Plan

## Objective

Define a research-backed ontology that can support personality/style modeling
without overclaiming.

## Core Model Layers

- observed evidence
- style preferences
- assessment responses and score results
- trait hypotheses
- context-specific modes
- motivations and values
- aesthetic preferences
- generation mappings
- sensitive or blocked inference categories

## Candidate Research Foundations

- Big Five / Five-Factor Model
- HEXACO
- CAPS
- Whole Trait Theory
- construct validity and psychometrics
- OCEAN assessment instruments under `assessments/ocean/`
- language-based personality inference
- digital footprint inference
- dimensional psychopathology for boundary design

## Profile Atom Requirements

Each profile atom should include:

- claim
- domain
- evidence
- source IDs
- context
- confidence
- stability
- recency
- counterevidence
- user confirmation status
- sensitivity level
- generation mappings

## Participant-Link MVP Distinction

The participant-link validation MVP may use assessment outcomes as
scenario-scoped candidate prediction context. That context is for testing a
predicted response, not for promoting assessment-derived atoms to active/global
profile controls. Alignment feedback should inform reviewed mapping decisions
and future model design, not silently change raw evidence or confidence.

## Open Questions

- Which constructs are useful enough for generation?
- Which constructs require explicit user self-report?
- Which constructs should never be stored?
- How should confidence be calibrated across data sources?
- How should assessment-derived atoms be versioned when scoring specs change?
