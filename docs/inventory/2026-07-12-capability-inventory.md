# Sol Capability Inventory

Inventory date: 2026-07-12

## Purpose

Provide a concrete inventory of the repository's product, research, data,
implementation, validation, and workflow assets. This document describes what
exists; it does not convert plans or experimental artifacts into completed
capabilities.

## Executive Snapshot

Sol currently has a strong local assessment-to-profile vertical slice and a
large research-support corpus. It does not yet have the complete Personal
Creative Style Kit.

Capability maturity:

| Area | Maturity | Summary |
|---|---|---|
| Research/RAG operations | Strong local foundation | Large lexical corpus, reviewed-card promotion workflow, import queues |
| Assessment acquisition | Strong prototype foundation | 11 permissive/open forms, 1,539 items, scoring metadata |
| Assessment administration | Working local MVP | Browser flow, persistence, scoring, evidence, correction, deletion |
| Profile atom lifecycle | Working local MVP | Provisional/active/suppressed states, review history, scoped export |
| Consent/data control | Working local MVP boundary | Persisted session consent, fingerprints, selective deletion; not source-level or multi-user |
| Generation | Early contract prototype | Eligible-context packet and model-free prompt dry run only |
| Evaluation | Minimal | Categorical feedback events; no baseline comparison or reporting |
| Creative Style Kit contracts/storage | Validated foundation | Five record schemas, cross-record validator, atomic local repository, local/mock ADR |
| Creative Style Kit inputs | Not implemented | No writing samples, examples, preferences, or moodboards |
| Original Sol assessment | Experimental design review | 30-item inactive candidate; no expert or empirical validation |
| Production platform | Not implemented | No auth, multi-user DB, deployment, provider operations, or observability |

## Repository Footprint

- Approximate working-tree size excluding Git metadata: 58 MB.
- Local RAG index: 23 MB, 20,600 chunks.
- Application UI: approximately 44 KB.
- Assessment data: approximately 488 KB.
- Research knowledge base: approximately 12 MB.
- Local JSON databases: approximately 2.7 MB.
- Tools: approximately 444 KB of Python.
- Tests: approximately 124 KB.
- Main implementation style: Python standard library backend/CLIs plus plain
  HTML, CSS, and browser JavaScript.
- Optional operator/development dependencies are declared in
  `requirements-dev.txt`; the main assessment and RAG runtime remains standard
  library based.

## Product And UX Inventory

### Local Browser Surface

Files:

- `app/assessment-mvp/index.html`
- `app/assessment-mvp/app.js`
- `app/assessment-mvp/styles.css`

Views:

- **Administer**: instrument selection, consent acknowledgment, session start,
  questionnaire, autosave, scoring, scores, atoms, session export/delete.
- **Workbench**: session summaries, aggregate atoms, lifecycle filters, evidence,
  atom correction, scoped context export, selective response/atom deletion.

Supported interactions:

- load one of 11 manifest instruments;
- start a consented local session;
- save and resume responses;
- score complete sessions;
- inspect score and item evidence;
- confirm, reject, or keep atoms review-only;
- edit a claim and add a user note;
- inspect original wording and review count;
- export/delete a session;
- delete raw responses or derived atoms separately;
- export default or review-inclusive profile context.

Not present:

- onboarding or user account model;
- writing-sample/example upload;
- direct generation-guidance editor;
- generation-run/output view;
- output comparison/evaluation UI;
- visual reference or moodboard flow;
- accessible production-grade component system;
- deployment, auth, tenancy, or audit console.

## Assessment Inventory

### Administrable Corpus

- 11 instruments.
- 186 scales.
- 1,539 stored items.
- 10 IPIP/public-domain instruments.
- 1 TIPI/permissive-use instrument.
- Supported scoring methods:
  - `sum_keyed_items` (10 instruments);
  - `average_two_items_per_domain` (TIPI).

Instrument families include:

- Big Five factor markers;
- Mini-IPIP and Mini-IPIP6;
- Big Five aspects;
- AB5C facets;
- IPIP NEO domain/facet representations;
- IPIP-NEO-120 variants;
- IPIP-NEO-60;
- TIPI.

Reference/license-review metadata includes seven entries covering BFI, BFI-2,
BFI-10, NEO, HEXACO, international mini-markers, and a single-item measure.

### Experimental Sol Candidate

- `Sol-OCEAN-Quick-v0`.
- 30 original candidate items.
- Five domains and 15 candidate subconstructs.
- One positive and one negative item per subconstruct.
- Explicit sensitivity, reading target, provenance, and failure-mode metadata.
- Exact normalized collision checking against stored instrument wording.
- Excluded from `assessments/ocean/manifest.json`.
- Rejected by product session/scoring boundaries.
- Not expert-reviewed, cognitively tested, piloted, reliable, valid, normed, or
  approved for product use.

## Assessment And Profile Runtime Inventory

### Scoring And Derivation

`tools/assessment_to_profile_atoms.py` provides:

- response-scale bounds and reverse scoring;
- raw and normalized domain scoring;
- user-facing score bands;
- reliability/item-count confidence heuristics;
- TIPI and reliability uncertainty notes;
- item-level evidence records;
- provisional assessment-derived profile atoms;
- an explicit guard against experimental candidate scoring.

### Session Store

`tools/assessment_session_store.py` provides:

- atomic same-directory JSON writes;
- serialized mutation inside the local server process;
- UTC timestamp normalization;
- response ID/value validation;
- instrument fingerprint enforcement;
- persisted consent receipt and scoring/instrument provenance for new sessions;
- immutable completed-session responses;
- reviewed-atom rescore protection;
- lifecycle invariant validation;
- session/profile summaries;
- atom review history and user notes;
- generation eligibility filtering;
- scoped context construction;
- generation feedback mapping notes;
- whole/selective deletion with feedback-reference cleanup.

Storage remains local, single-process JSONDB. Historical tracked sessions
predate some newer integrity fields and remain readable without fabricated
provenance.

### Profile Atom Contract

`kb/model/profile_atom_schema_v0.md` defines:

- observation/candidate/active/suppressed lifecycle;
- `review_only`, `contextual`, and `global` activation scope;
- evidence, source IDs, context, confidence, stability, recency, sensitivity;
- original and edited claims;
- user feedback, notes, and append-only review history;
- generation mappings and mapping feedback notes;
- counterevidence and user visibility.

### Creative Style Kit Repository

`tools/style_kit_store.py` provides:

- a repository protocol and local JSON implementation;
- environment-selected storage with an ignored `tmp/` default;
- empty reads without filesystem side effects;
- create/read/list/replace operations for all five record collections;
- complete bundle validation before every write;
- atomic replacement and in-process mutation serialization;
- defensive copies and explicit corruption/unsupported-operation errors;
- user-only permissions on created repository files.

It remains single-process and has no routes or product UI.

## API Inventory

The local HTTP server exposes JSON/static routes for:

- health;
- assessment manifest and instrument retrieval;
- session creation/list/show/export;
- response save and scoring;
- atom review;
- aggregate profile atoms;
- scoped profile-context export;
- generation-feedback creation;
- whole-session deletion;
- response-only deletion;
- profile-atom-only deletion.

Boundary: local exploratory use only. There is no authentication,
authorization, CSRF strategy, tenant isolation, database transaction layer, or
production deployment contract.

## Generation Inventory

### Existing

- `profile-context-packet` schema and ADR;
- filtering for confirmed/edited, active, contextual/global, non-blocked atoms;
- explicit exclusion of review-only candidates from generation eligibility;
- `tools/generation_pilot.py` model-free writing-guide prompt dry run;
- system/user message separation and embedded-instruction handling;
- feedback values: accurate, useful, too strong, too generic, wrong;
- provenance-linked generation mapping notes;
- documented model-backed gate review;
- explicit proposed/confirmed/edited/disabled guidance lifecycle;
- shared profile-atom generation-eligibility policy;
- immutable original guidance plus field-level prompt-safe review history;
- observation/profile-atom evidence checks and context/task filtering.

### Missing Gate Conditions

- browser/API generation-guidance authoring;
- persisted pilot-run records;
- feedback enforcement against a known run and exact atoms used;
- provider abstraction and explicit external-model opt-in;
- local/mock provider exercising the same contract as a future real provider;
- output schema and safety validator;
- user-visible generated artifact;
- generic baseline comparison;
- output evaluation/reporting.

## Research And RAG Inventory

### Registries And Reviewed Knowledge

- 13 base source registry entries.
- 34 adjacent-source registry entries.
- 15 Markdown source/review cards.
- Core model documents for knowledge shape, signal permissions, and profile
  atoms.
- Reviewed anchors for Big Five, HEXACO, CAPS, Whole Trait Theory, construct
  validity, language/digital signals, workspace architecture, and clinical
  boundary frameworks.

### Background Corpus

- 1,261 Wikipedia summary cards.
- 1,766 paper metadata cards.
- 3,386 import queue records.
- 3,089 imported queue records.
- 283 pending paper references, all title-only.
- 7 pending Wikipedia term records and 7 rejected mappings.
- Paper review state: 21 rejected, 31 deferred, 14 manual mappings.

Metadata cards and Wikipedia summaries are background retrieval material, not
reviewed product knowledge.

### Retrieval

`tools/rag.py` provides:

- Markdown/JSON chunking;
- 20,600-chunk generated index;
- local BM25-style search;
- snippet and full-context output;
- no external API or embedding dependency.

Missing:

- retrieval relevance benchmark;
- citation/answer evaluation harness;
- automated stale-index detection;
- hybrid or semantic retrieval (appropriately deferred until measured need).

## Import And Curation Inventory

`tools/kb_importer.py` provides:

- Crossref DOI and conservative title resolution;
- manual match support;
- Wikipedia term/link queueing and slow serialized import;
- retry/rate-limit handling;
- per-item queue checkpointing;
- review-state application and review reports;
- metadata-card generation.

`tools/import_ocean_assessments.py` provides operator-driven normalization of
downloaded official assessment HTML and requires `beautifulsoup4`.

## Documentation And Decision Inventory

- 16 numbered product/research plan documents (`00` through `15`).
- Six ADRs for RAG, queueing, profile lifecycle, scoped context, session
  integrity, and Creative Style Kit record ownership.
- Assessment architecture documents for acquisition, scoring, storage, web,
  evidence, context export, generation, and experimental candidates.
- Research-promotion and RAG-structure documents.
- One full initial-plan/progress audit.
- Maintained project memory and current-state handoff.
- Main README with product snapshot, commands, roadmap, and boundaries.

## Reusable Agent Workflows

Repo-local `.codex` skills:

- `sol-research-kb-workflow`;
- `sol-experimental-assessment-workflow`.

Additional repository skill package:

- `skills/personality-rag-research` with source-card standards.

Guidance files:

- root `AGENTS.md`;
- `assessments/AGENTS.md`;
- `kb/AGENTS.md`.

## Validation Inventory

### Automated

45 unittest cases cover:

- session lifecycle and isolated JSONDB behavior;
- consent/instrument provenance;
- response contracts and concurrent mutations;
- scoring confidence and evidence for TIPI/Mini-IPIP;
- lifecycle validation, editing, history, and persistence;
- API route lifecycle and deletion;
- static UI contracts and responsive CSS guards;
- scoped context filtering;
- model-free generation safety and feedback;
- experimental candidate structure, collision, manifest, and activation guards;
- Creative Style Kit schemas, ownership, references, guidance eligibility,
  deletion redaction, and external-provider rejection;
- Style Kit read-after-write, invalid-write atomicity, defensive copies,
  environment isolation, corruption handling, and in-process concurrency;
- guidance transitions, edits/history, prompt-safe separation, evidence
  eligibility, atom exclusions, filtering, and disabling.

### Rendered

- desktop/mobile Administer screenshots;
- desktop/mobile Workbench screenshots;
- isolated temporary session DB;
- tracked-session immutability check.

### Missing

- browser automation for full interactive flows and expanded evidence/edit
  states;
- accessibility audit;
- fuzz/property testing of storage contracts;
- performance/load testing;
- production security testing;
- retrieval-quality evaluation;
- generation-output evaluation.

## Tracked Examples And Generated Assets

- TIPI and Mini-IPIP sample response fixtures.
- Two tracked assessment-run session/summary artifact pairs.
- Two tracked sample sessions in JSONDB.
- Generated RAG and visual-QA artifacts are ignored.

Some tracked sample sessions/artifacts predate the latest consent and evidence
shape. They are historical examples, not canonical current-schema golden files.

## Current Constraints And Debt

1. Product value has not been demonstrated against a generic generation
   baseline.
2. The original wedge's direct style evidence is absent.
3. Broad assessment traits have weak direct linkage to generation behavior.
4. Generation is contract-only and model-free.
5. Pilot-run provenance is absent.
6. Evaluation events/reporting are incomplete.
7. JSONDB is intentionally single-process/local.
8. Historical assessment artifacts remain intentionally labeled examples of an
   earlier schema rather than current golden fixtures.
9. Research volume substantially exceeds reviewed-card coverage.
10. Experimental assessment work is externally blocked on qualified review and
    participant evidence.

## Honest Capability Statement

Sol can honestly claim a local, safety-conscious assessment MVP that produces
inspectable, user-correctable profile candidates and a scoped context packet
for model-free generation experiments.

It should not yet claim a complete Creative Style Kit, validated original
assessment, personalized-output benefit, production privacy/security posture,
or multimodal platform.
