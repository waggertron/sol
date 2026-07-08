# Current State

Last updated: 2026-07-08

## Project Status

Sol is currently a research-first repository for a user-consented personality
and style modeling platform. The repo now has three concrete foundations:

- an internal RAG knowledge base for research, planning, source cards, and
  imported summaries
- a JSONDB queue for tracking future research and Wikipedia imports
- an OCEAN assessment area with permissive/open instruments and scoring metadata

There is now a local browser-based MVP web app. The current product build uses
the stored assessment instruments as the first administrable flow.

## Current Corpus

- RAG index: 20,600 chunks
- Base source registry: 13 sources
- Adjacent source registry: 34 sources
- Source cards: 13 Markdown cards
- Wikipedia summary imports: 1,261 background cards
- Paper metadata imports: 1,646 background cards
- Import queue: 3,373 total queue entries
- Imported queue entries: 3,076
- Pending paper references: 283
- Pending paper references with DOI: 0
- Pending title-only paper references: 283
- Paper review rejections: 21
- Paper review deferrals: 31
- Paper manual mappings: 2
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
and 2 manual mappings
that resolved the former DOI-backed failures. The remaining paper tail should
be managed as a review/resolution queue rather than a bulk-ingestion batch.
The consciousness / global-workspace cluster around Bernard Baars has now also
been imported into `kb/paper_imports/` and distilled into reviewed source cards
at `kb/cards/baars_global_workspace_theory.md` and
`kb/cards/dehaene_workspace_neuroscience.md`. Those cards now inform
thresholding, candidate-vs-active atoms, and context activation in the model
docs.

## Current Product Direction

The first product wedge remains the Personal Creative Style Kit, but the
immediate implementation path remains assessment-first:

1. Administer a permissive OCEAN instrument.
2. Store responses and score results with instrument-version provenance.
3. Convert scores into editable, non-diagnostic profile atom candidates.
4. Present results with uncertainty and user correction controls in the local
   web MVP.
5. Export or delete local assessment sessions when needed.
6. Review profile atoms across sessions in the workbench.
7. Use confirmed atoms as scoped context for future generation experiments.

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

## Safety Posture

The project still forbids diagnosis, protected-class inference, hidden
profiling, eligibility decisions, and clinical personality-disorder labeling.
Assessment results should be treated as self-report evidence, not fixed identity
claims.
