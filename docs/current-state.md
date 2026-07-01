# Current State

Last updated: 2026-07-01

## Project Status

Sol is currently a research-first repository for a user-consented personality
and style modeling platform. The repo now has three concrete foundations:

- an internal RAG knowledge base for research, planning, source cards, and
  imported summaries
- a JSONDB queue for tracking future research and Wikipedia imports
- an OCEAN assessment area with permissive/open instruments and scoring metadata

There is not yet an MVP web app. The next product build should use the stored
assessment instruments as the first administrable flow.

## Current Corpus

- RAG index: 2,100 chunks
- Base source registry: 13 sources
- Adjacent source registry: 34 sources
- Source cards: 13 Markdown cards
- Wikipedia summary imports: 102 background cards
- Paper metadata imports: 25 background cards
- Import queue: 3,373 total queue entries
- Imported queue entries: 219
- Pending paper references: 1,904
- Pending linked Wikipedia articles: 1,236
- Rejected Wikipedia mappings: 7
- Queued Wikipedia retry notes from latest rate limit: 30

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

Current queue ingestion support:

- `import-queued-wikipedia` imports pending linked Wikipedia summaries.
- `import-paper-metadata` imports Crossref bibliographic metadata for queued
  DOI references.
- Wikimedia/Wikipedia imports now default to a conservative serialized cadence:
  one request every 12 seconds, no parallel jobs, stop on HTTP `429` or `503`
  after respecting `Retry-After` or the configured delay.

Paper imports are metadata-only by default. Full paper text and abstracts are
not imported without separate review.

## Current Product Direction

The first product wedge remains the Personal Creative Style Kit, but the
immediate implementation path is now assessment-first:

1. Administer a permissive OCEAN instrument.
2. Store responses and score results with instrument-version provenance.
3. Convert scores into editable, non-diagnostic profile atom candidates.
4. Present results with uncertainty and user correction controls.
5. Use confirmed atoms as scoped context for future generation experiments.

Recommended first MVP instruments:

- `tipi.json` for the fastest end-to-end flow test
- `mini_ipip.json` for a short OCEAN assessment path
- `ipip_neo_60_maples_keller_2019.json` for a compact NEO-domain path

## Safety Posture

The project still forbids diagnosis, protected-class inference, hidden
profiling, eligibility decisions, and clinical personality-disorder labeling.
Assessment results should be treated as self-report evidence, not fixed identity
claims.
