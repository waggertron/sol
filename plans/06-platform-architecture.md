# Platform Architecture Plan

## Objective

Define the reusable platform primitives behind the first product wedge.

## Candidate Services

- data ingestion
- consent and permissions
- assessment administration
- scoring engine
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

1. User grants source permission, uploads samples, or starts an assessment.
2. Ingestion or assessment administration records provenance.
3. Extraction or scoring creates observations.
4. Inference proposes profile atoms.
5. User confirms or corrects atoms.
6. Generation uses scoped atoms.
7. Feedback updates atom confidence and generation mappings.

## Current MVP Direction

The assessment-first MVP now loads stored instruments, administers and scores
them, persists consent/version provenance for new sessions, creates editable
profile atoms, explains evidence, and exports scoped context. The next
architecture work should remain wedge-driven: generation-guidance authoring,
persisted pilot runs, and one consented writing-sample ingestion path.

## Open Questions

- Should profile inference be batch, streaming, or hybrid?
- How should profile atoms be versioned?
- What is the boundary between evidence storage and generated summaries?
- Which parts must be local-first or privacy-preserving?
- Which storage layer should replace JSON files once assessment sessions become
  multi-user?
