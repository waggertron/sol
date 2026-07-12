# Current State

Last updated: 2026-07-12

## Project Status

Sol is currently a research-first repository for a user-consented personality
and style modeling platform. The repo now has three concrete foundations:

- an internal RAG knowledge base for research, planning, source cards, and
  imported summaries
- a JSONDB queue for tracking future research and Wikipedia imports
- an OCEAN assessment area with permissive/open instruments and scoring metadata

There is now a local browser-based MVP web app. The current product build uses
the stored assessment instruments as the first administrable flow.

The current browser QA baseline includes both automated route checks and
rendered desktop/mobile screenshot verification for the Administer and
Workbench views.

## Current Corpus

- RAG index: 20,600 chunks
- Base source registry: 13 sources
- Adjacent source registry: 34 sources
- Source cards: 15 Markdown cards
- Wikipedia summary imports: 1,261 background cards
- Paper metadata imports: 1,766 background cards
- Import queue: 3,386 total queue entries
- Imported queue entries: 3,089
- Pending paper references: 283
- Pending paper references with DOI: 0
- Pending title-only paper references: 283
- Paper review rejections: 21
- Paper review deferrals: 31
- Paper manual mappings: 14
- Pending linked Wikipedia articles: 0
- Pending direct Wikipedia term matches: 7
- Rejected Wikipedia mappings: 7
- Queued Wikipedia retry notes from latest rate limit: 0

## Assessment Area

The current assessment repository lives under:

- `assessments/`
- `assessments/ocean/`

Current OCEAN acquisition:

- 11 stored instruments
- 186 scales
- 1,539 stored items

Experimental design work:

- 1 project-authored candidate outside the administrable manifest
- `Sol-OCEAN-Quick-v0`: 30 items, 5 domains, 15 candidate subconstructs
- status: design review only; no reliability, validity, norms, or product use

Stored instruments include:

- IPIP Goldberg Big-Five Factor Markers
- Mini-IPIP
- Mini-IPIP6
- IPIP Big Five Aspects Scales
- IPIP AB5C 45 Facets
- IPIP NEO-PI-R domain representation
- IPIP NEO-PI-R facet representation
- IPIP-NEO-120 Johnson 2014
- IPIP-NEO-120 Maples et al. 2014
- IPIP-NEO-60 Maples-Keller et al. 2019
- Ten Item Personality Inventory

Reference-only or license-review instruments are tracked in:

- `assessments/ocean/reference_only/ocean_reference_inventory.json`

## Current Tooling

- `tools/rag.py` builds and searches the local lexical RAG index.
- `tools/kb_importer.py` manages the research import queue and Wikipedia /
  Crossref imports.
- `tools/import_ocean_assessments.py` normalizes downloaded official OCEAN
  assessment pages into the `assessments/ocean/` JSON format.
- `tools/assessment_to_profile_atoms.py` converts stored assessment responses
  into scored results plus `profile_atom_schema_v0`-aligned provisional profile
  atoms.
- `tools/assessment_session_store.py` persists assessment sessions, raw
  responses, derived scores, and provisional profile atoms in local JSONDB
  storage.
- `tools/run_assessment_mvp.py` runs the current end-to-end local assessment
  MVP flow and writes export artifacts for later UI integration.
- `tools/assessment_web_mvp.py` serves the current local browser flow and a
  thin JSON API over the same session store. The UI now includes assessment
  administration, session export/delete controls, and a cross-session profile
  atom workbench.
- Profile atom review now supports provenance-preserving claim edits, user
  notes, lifecycle/scope changes, and timestamped field-level review history.
- Score and atom cards now expose expandable calculation evidence, instrument
  and source context, item response/keying details, and non-diagnostic
  uncertainty cautions for TIPI and reliability-bearing instruments.
- The workbench exports a scoped profile context packet. Default export includes
  only confirmed/edited, active contextual/global atoms with non-blocked
  sensitivity; rejected and suppressed atoms are always excluded, and opt-in
  review candidates are marked generation-ineligible.
- Phase 5 has started with a model-free writing and communication guide dry run.
  It renders the reviewed prompt and generation-eligible packet context without
  calling an external model; optional artifacts are restricted to ignored
  `tmp/generation-pilot/` storage.
- Structured pilot feedback supports `accurate`, `useful`, `too_strong`,
  `too_generic`, and `wrong`. Events add provenance-linked, append-only
  generation-guidance notes without automatically changing raw responses,
  claims, or confidence.
- The prompt and feedback contract review is complete. Model-backed execution
  is not yet approved. Domain-level guidance, persisted dry-run/mock runs,
  output validation, and run-bound blinded evaluation now exist; remaining
  gates include browser/API authoring, external-provider opt-in, and the
  eventual provider-request exclusion test.
- The assessment session boundary now validates response IDs/values, persists
  consent and exact instrument/scoring provenance for new sessions, uses
  serialized atomic JSON writes, protects reviewed atoms from rescoring, and
  supports separate deletion of raw responses and derived atoms.
- Original Sol OCEAN design work now includes a reviewed-source-backed
  construct blueprint, a 30-item experimental candidate, and a validator for
  structure, balanced keying, required risk metadata, manifest exclusion, and
  exact wording collisions. Expert and empirical review remain open.
- A repo-local `sol-experimental-assessment-workflow` skill now preserves the
  blueprint-first, manifest-excluded, validation-gated process for future
  original assessment work.
- Creative Style Kit Phase 0 now defines independent, versioned source,
  observation, generation-guidance, pilot-run, and evaluation-event contracts.
  The offline validator checks JSON Schema shape plus ownership, provenance,
  hashes, references, deletion state, generation eligibility, and external-mode
  exclusion. No tracked or UI-created Style Kit product data exists yet.
- Optional operator/development dependencies are declared in
  `requirements-dev.txt`; production assessment and RAG paths remain standard
  library based.
- `tools/style_kit_store.py` now provides the first Creative Style Kit
  persistence boundary: an environment-selectable, atomic, single-process local
  JSON repository that validates the full record graph before each mutation and
  returns defensive copies. Its default manual path is ignored
  `tmp/style-kit/style-kit-records.json`; no routes or UI use it yet.
- `tools/style_kit_guidance.py` now provides explicit proposed/confirmed/edited/
  disabled guidance transitions, immutable original instructions, separate
  prompt-safe edit history, evidence eligibility checks, and context/task
  filtering. `tools/profile_atom_policy.py` is the shared eligibility predicate
  used by both assessment context export and Style Kit guidance.
- `tools/style_kit_pilot.py` now persists generic/personalized run pairs through
  credential-free dry-run and deterministic mock providers. Runs bind the exact
  task, requested context, consent/source refs, versioned prompt-safe guidance
  snapshot, atom refs, provider/prompt versions, request/context/output hashes,
  UTC timestamps, and output validation state. Failed unsafe output is redacted.
- `tools/style_kit_evaluation.py` now enforces a persisted two-step blinded
  lifecycle: store an opaque choice first, then reveal identity and record
  ratings/correction later. Events are limited to active completed mock runs and
  exact used guidance, and deletion redacts feedback without mutating evidence,
  guidance, runs, or assessment data.

Current queue ingestion support:

- `import-queued-wikipedia` imports pending linked Wikipedia summaries.
- `import-paper-metadata` imports Crossref bibliographic metadata for queued
  DOI references.
- `import-paper-manual-matches` imports only manually curated paper mappings.
- `apply-paper-review` applies persisted defer/reject decisions for unresolved
  paper references.
- `paper-review-report` writes the current unresolved paper tail to
  `kb/research/paper_review_queue.md` for manual curation.
- Wikimedia/Wikipedia imports now default to a conservative serialized cadence:
  one request every 12 seconds, no parallel jobs, stop on HTTP `429` or `503`
  after respecting `Retry-After` or the configured delay.
- Wikipedia import commands now emit per-item progress logs by default; pass
  `--no-progress` only when a quiet JSON-only run is needed.
- Wikipedia queue imports checkpoint `jsondb/import_queue.json` after each
  attempted item so interrupted long runs do not leave generated files and queue
  records out of sync.
- All current `wikipedia_article` queue records have been imported. Remaining
  Wikipedia backlog is now mostly review work on a small number of linked or
  search-derived candidates rather than another large queue drain.

Paper imports are metadata-only by default. Full paper text and abstracts are
not imported without separate review. The importer now supports Crossref
title-search fallback as well as DOI lookups, with stricter title-match
scoring and a persisted paper review DB for manual defer/reject/manual-DOI
decisions. The current paper review pass has already carved out 21 obvious
journal-title-only or series-title-only rejects, 31 manual-review deferrals,
and 14 manual mappings. Two resolved the former DOI-backed failures; the others
include later curated source-cluster imports. The remaining paper tail should
be managed as a review/resolution queue rather than a bulk-ingestion batch.
The consciousness / global-workspace cluster around Bernard Baars has now also
been imported into `kb/paper_imports/` and distilled into reviewed source cards
at `kb/cards/baars_global_workspace_theory.md` and
`kb/cards/dehaene_workspace_neuroscience.md`. Those cards now inform
thresholding, candidate-vs-active atoms, and context activation in the model
docs.

## Current Product Direction

The assessment-first foundation now proves administration, evidence,
correction, lifecycle controls, and scoped context export. The next product
proof returns to the Personal Creative Style Kit itself:

1. Add browser guidance, run-history, comparison, and evaluation surfaces.
2. Ingest authorized writing samples and direct style preferences as the
   primary product evidence.
3. Present localized observations and editable, context-specific guidance.
4. Compare personalized and generic short text artifacts blind.
5. Gate any real-model, visual, or platform expansion on safety and measured
   product value.

OCEAN assessment remains optional context. Broad traits are not direct global
generation controls, and the inactive Sol candidate is not part of this path.

The full capability inventory and active roadmap live at:

- `docs/inventory/2026-07-12-capability-inventory.md`
- `plans/14-personal-creative-style-kit-roadmap.md`

The first implementation-facing assessment output contract now lives at:

- `docs/architecture/assessments/profile-atom-output.md`
- `docs/architecture/assessments/session-storage.md`
- `docs/architecture/assessments/mvp-flow.md`
- `docs/architecture/assessments/web-mvp.md`

The first sample response fixture for end-to-end testing lives at:

- `assessments/ocean/examples/tipi_sample_responses.json`

Recommended first MVP instruments:

- `tipi.json` for the fastest end-to-end flow test
- `mini_ipip.json` for a short OCEAN assessment path
- `ipip_neo_60_maples_keller_2019.json` for a compact NEO-domain path

Run the current web MVP with:

```bash
python3 tools/assessment_web_mvp.py --port 8765
```

Then open `http://127.0.0.1:8765`.

## Current Handoff

- Browser QA is currently green at the routed and rendered levels.
- Profile atom editing with provenance preservation is complete.
- Inspectable evidence and uncertainty views are complete.
- Scoped profile context export is complete.
- The earlier assessment-context prompt dry run remains available; the new Style
  Kit boundary now also persists generic/personalized dry-run and mock records.
- Creative Style Kit Phase 0 plus Increments 1-4 are complete and validated by
  the 61-test suite.
- The recorded stopping point is the boundary after Increment 4. Increment 5 is
  explicitly unstarted; resume with the browser guidance, run-history, blinded
  comparison, and evaluation workbench in
  `plans/15-style-kit-validated-execution.md`.
- Model-backed execution remains deferred until after the local closed loop and
  product-evaluation gate.
- Experimental Sol OCEAN follow-up is limited to expert/cognitive review and a
  later validation-gated pilot; the candidate is not active in the MVP.

## Safety Posture

The project still forbids diagnosis, protected-class inference, hidden
profiling, eligibility decisions, and clinical personality-disorder labeling.
Assessment results should be treated as self-report evidence, not fixed identity
claims.
