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

- RAG index: 1,800 chunks
- Base source registry: 13 sources
- Adjacent source registry: 34 sources
- Source cards: 13 Markdown cards
- Wikipedia summary imports: 82 reviewed cards
- Import queue: 3,373 total queue entries
- Imported queue entries: 174
- Pending paper references: 1,929
- Pending linked Wikipedia articles: 1,256
- Rejected Wikipedia mappings: 7

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
