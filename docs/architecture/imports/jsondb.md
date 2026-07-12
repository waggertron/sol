# JSONDB Import Architecture

## Purpose

The JSONDB import layer tracks discovered knowledge candidates before they are
promoted into reviewed KB content.

It supports:

- paper references discovered from Crossref metadata
- Wikipedia articles matched from term inventory
- linked Wikipedia articles discovered from imported pages
- assessment inventory metadata and links into the assessment repository
- local assessment session storage for MVP scoring and profile-atom generation
- import run logs
- `imported: false` status for future import runs

## Files

```text
jsondb/
  assessment_inventory.json
  assessment_sessions.json
  term_inventory.json
  import_queue.json
  import_runs.json
  wiki_import_review.json
  paper_import_review.json
```

Current queue snapshot is summarized in `docs/current-state.md`.

The unresolved paper-review tail is summarized in
`kb/research/paper_review_queue.md`.

## Queue Item Shape

```json
{
  "id": "paper:10.1037/...",
  "kind": "paper_reference",
  "title": "Source title",
  "doi": "10.1037/...",
  "url": "https://doi.org/10.1037/...",
  "discovered_from": ["source_id"],
  "imported": false,
  "imported_path": null,
  "priority": "normal",
  "notes": []
}
```

## Import States

- `imported: false` means discovered but not reviewed into the KB.
- `imported: true` means a reviewed KB artifact exists.
- `imported_path` should point to the reviewed artifact when available.

## Tooling

Use:

```bash
python3 tools/kb_importer.py run-initial --wiki-limit 40 --reference-limit 500
```

Subcommands:

- `init-db`
- `import-wikipedia`
- `import-queued-wikipedia`
- `import-paper-metadata`
- `import-paper-manual-matches`
- `queue-crossref-references`
- `run-initial`
- `sync-wikipedia-terms`
- `apply-wiki-review`
- `apply-paper-review`
- `paper-review-report`
- `clean-notes`

Assessment imports are handled separately by:

```bash
python3 tools/import_ocean_assessments.py --source-dir /path/to/downloaded/html
```

The assessment inventory links JSONDB metadata to concrete stored instruments
under `assessments/ocean/`.

Assessment session persistence is handled by:

```bash
python3 tools/assessment_session_store.py init-db
```

That file stores local response sessions, derived scores, and provisional
profile atoms for the assessment-first MVP.

## Queue Ingestion Policy

Wikipedia queue items can be imported as summary cards under `kb/wiki_imports/`.
These are background references, not peer-reviewed evidence.

Queued paper DOI references can be imported as metadata-only cards under
`kb/paper_imports/`. These cards intentionally omit full paper text and
abstracts until a human review promotes the source into a source card.

Current queue snapshot:

- 1,338 imported queue records with `kind: wikipedia_article` or
  `wikipedia_linked_article`
- 7 pending `wikipedia_term` records
- 1,766 paper metadata cards
- 283 pending `paper_reference` records
- 0 pending DOI-backed `paper_reference` records
- 283 pending title-only `paper_reference` records
- 7 rejected Wikipedia mappings tracked in `wiki_import_review.json`

Paper review state is persisted separately in `paper_import_review.json`:

- `rejected_items`: queue records that should stop retrying
- `deferred_items`: items intentionally parked for later manual work
- `manual_matches`: queue records with human-approved DOI mappings

Current seeded paper review state:

- 21 rejected journal-title-only or series-title-only records
- 31 deferred records for books, manuals, edited volumes, in-press references,
  or clearly non-Crossref-friendly reference works
- 14 manual mappings, including nonstandard DOI resolution and curated
  source-cluster imports

Example:

```json
{
  "version": 1,
  "rejected_items": [
    {
      "id": "paper-title:communication_research",
      "title": "Communication Research",
      "reason": "Journal title only, not a resolvable cited work."
    }
  ],
  "deferred_items": [
    {
      "id": "paper-title:neo_pi_r_professional_manual",
      "title": "NEO PI-R professional manual",
      "reason": "Likely book/manual; requires manual catalog lookup."
    }
  ],
  "manual_matches": [
    {
      "id": "paper-title:some_title",
      "title": "Some title",
      "doi": "10.0000/example",
      "reason": "Human-confirmed DOI after manual review."
    }
  ]
}
```

The latest slow serialized queue drains at one request every 12 seconds
imported 1,214 queued Wikipedia records without rate limiting. That completed
the current importable Wikipedia-article backlog; what remains now is the small
set of direct term matches under manual review.

Paper ingestion now supports both direct DOI imports and Crossref title-search
fallback, with stricter matching heuristics and a persisted review path for the
remaining tail. That cleared the entire DOI-backed bulk backlog and most of the
former title-only backlog, bringing the paper corpus to 1,766 metadata-only
cards. The remaining backlog is a small unresolved tail of 283 records, now
entirely title-only references.

## Wikimedia Rate Policy

Use slow, serial imports for Wikimedia/Wikipedia API calls. The project default
is one request every 12 seconds, which is intentionally below the lowest
published 2026 Wikimedia API bucket for unidentified clients.

Recommended queue-drain command:

```bash
python3 tools/kb_importer.py import-queued-wikipedia --limit 20 --link-limit 0 --sleep 12
```

Operational rules:

- Do not run parallel Wikipedia import jobs.
- Keep linked-article expansion disabled with `--link-limit 0` unless the goal
  is to grow the queue.
- Progress logs are enabled by default for Wikipedia import commands and are
  written to stderr; use `--no-progress` only for quiet JSON-only runs.
- Queue imports checkpoint `jsondb/import_queue.json` after each attempted item
  so interrupted long runs can be resumed without losing queue state.
- If Wikimedia returns HTTP `429` or `503`, respect `Retry-After` when present,
  wait at least the configured sleep interval, and stop the batch.
- Retry later at `--sleep 30` if `429` repeats.
- Treat Wikipedia imports as background summaries only.

References:

- <https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits>
- <https://www.mediawiki.org/wiki/API:Etiquette>

## Policy

Wikipedia article imports store summaries and source links by default. Full
article content should be handled only through a separate licensed-content
workflow with attribution and share-alike implications documented.
