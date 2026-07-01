# JSONDB Import Architecture

## Purpose

The JSONDB import layer tracks discovered knowledge candidates before they are
promoted into reviewed KB content.

It supports:

- paper references discovered from Crossref metadata
- Wikipedia articles matched from term inventory
- linked Wikipedia articles discovered from imported pages
- assessment inventory metadata and links into the assessment repository
- import run logs
- `imported: false` status for future import runs

## Files

```text
jsondb/
  assessment_inventory.json
  term_inventory.json
  import_queue.json
  import_runs.json
  wiki_import_review.json
```

Current queue snapshot is summarized in `docs/current-state.md`.

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
- `queue-crossref-references`
- `run-initial`
- `sync-wikipedia-terms`
- `apply-wiki-review`
- `clean-notes`

Assessment imports are handled separately by:

```bash
python3 tools/import_ocean_assessments.py --source-dir /path/to/downloaded/html
```

The assessment inventory links JSONDB metadata to concrete stored instruments
under `assessments/ocean/`.

## Policy

Wikipedia article imports store summaries and source links by default. Full
article content should be handled only through a separate licensed-content
workflow with attribution and share-alike implications documented.
