# Plan of Plans

## Working Objective

Build a platform that turns user-consented data into an evidence-backed,
user-correctable personality and style model, then uses that model to guide
multimodal generation.

## Planning Principle

Start with one narrow subject feature set that proves the complete loop, then
extract reusable platform primitives.

Current first wedge:

> Personal Creative Style Kit

Current implementation state:

- research RAG scaffold is built and indexes `kb/`, `sources/`, `jsondb/`,
  `assessments/`, `docs/`, `plans/`, and the root README
- JSONDB import queue is active for papers and Wikipedia imports
- OCEAN assessment repository is populated with permissive/open instruments
- local assessment web MVP, profile workbench, automated QA, and rendered
  desktop/mobile QA are built
- profile atoms can be confirmed, rejected, kept review-only, or edited while
  preserving their original generated claim and review history
- assessment results and atoms have expandable score, item-level, instrument,
  source, and uncertainty evidence views
- the workbench exports a scoped, generation-safe profile context packet with
  explicit review-only inclusion for internal testing
- a model-free writing/communication guide pilot renders the reviewed prompt
  and eligible context locally
- structured pilot feedback produces provenance-linked generation-guidance
  notes without silently changing assessment evidence or confidence
- deterministic Style Kit pilot runs now support a persisted two-step blinded
  evaluation lifecycle bound to the exact run and guidance used
- the fastest validation path is now the participant-link scenario MVP in
  `16-participant-link-validation-mvp.md`: a no-auth shared link, opaque
  participant ID, fictional writing scenario, organic response, assessment,
  assessment-informed predicted response, response ranking, and alignment
  feedback
- hosting for that validation path is planned in
  `17-validation-mvp-hosting.md`, using Vercel for the public participant link
  and stateless API with hosted Postgres for durable pilot data
- original Sol OCEAN design work has a 30-item, manifest-excluded experimental
  candidate with a construct blueprint and structural/collision validator;
  expert and empirical validation remain open

See `docs/current-state.md` for current counts.

## Plan Set

### 1. Product Vision

Define the product thesis, target users, core value, and boundaries.

Output:

- product one-liner
- target user segments
- use cases
- non-goals
- ethical boundaries

### 2. First Wedge

Define the first concrete feature set.

Output:

- user journey
- input data requirements
- generated outputs
- profile editing surface
- MVP scope
- expansion triggers

### 3. Knowledge Model

Define the research-backed ontology used to evaluate profile feasibility.

Output:

- construct inventory
- profile atom schema
- confidence model
- context model
- construct validity requirements
- source evidence map

### 4. Data and Consent

Define what data can be used, how consent works, and how users control the
profile.

Output:

- data source matrix
- consent UX requirements
- provenance rules
- deletion/export rules
- sensitive inference gates

### 5. RAG Research

Build the internal research knowledge base.

Output:

- source registry
- source card format
- retrieval workflow
- research backlog
- paper ingestion process
- evidence grading

### 6. Platform Architecture

Define reusable services and boundaries.

Output:

- data ingestion layer
- consent service
- feature extraction pipeline
- profile service
- generation orchestrator
- feedback loop
- audit and deletion system

### 7. Evaluation and Safety

Define how to measure usefulness, validity, and risk.

Output:

- MVP evaluation protocol
- user study plan
- "feels like me" metrics
- correction-rate metrics
- blocked-use policy
- safety review checklist

### 8. OCEAN Assessment Path

Define the assessment-first MVP path for OCEAN self-report calibration.

Output:

- assessment inventory
- stored permissive/open instruments
- scoring metadata
- assessment-to-profile atom mapping
- MVP administration and scoring requirements

## Immediate Next Steps

1. Build the participant-link voice validation MVP before the full Style Kit
   workbench: shared link, participant ID, scenario response, assessment,
   predicted response, ranking, and alignment feedback.
2. Use the pilot to decide whether assessment-informed writing can sound like
   the participant before investing in richer source intake and observation
   dashboards.
3. Keep experimental OCEAN review as a parallel validation track rather than a
   dependency of the Creative Style Kit.

Execution ledgers:

- `14-personal-creative-style-kit-roadmap.md` (current product roadmap)
- `15-style-kit-validated-execution.md` (current validated implementation ledger)
- `16-participant-link-validation-mvp.md` (fast real-user validation slice)
- `17-validation-mvp-hosting.md` (Vercel hosting plan for the validation slice)
- `12-post-audit-roadmap.md`
- `13-sol-ocean-experimental-assessment.md` (parallel validation track)
