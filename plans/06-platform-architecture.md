# Platform Architecture Plan

## Objective

Define the reusable platform primitives behind the first product wedge.

## Candidate Services

- data ingestion
- consent and permissions
- source normalization
- feature extraction
- profile atom store
- inference engine
- user correction interface
- generation orchestrator
- modality adapters
- feedback loop
- audit, deletion, and export

## First Architecture Hypothesis

The product layer should not own the personality model. It should request a
scoped profile from a profile service and submit feedback after generation.

## Initial Data Flow

1. User grants source permission or uploads samples.
2. Ingestion normalizes data and records provenance.
3. Extraction creates observations.
4. Inference proposes profile atoms.
5. User confirms or corrects atoms.
6. Generation uses scoped atoms.
7. Feedback updates atom confidence and generation mappings.

## Open Questions

- Should profile inference be batch, streaming, or hybrid?
- How should profile atoms be versioned?
- What is the boundary between evidence storage and generated summaries?
- Which parts must be local-first or privacy-preserving?

