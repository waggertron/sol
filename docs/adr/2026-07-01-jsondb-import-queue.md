# 2026-07-01: JSONDB Import Queue

## Problem Statement

The knowledge base now needs to expand beyond manually curated source cards.
Each imported paper can reference many additional papers, and each Wikipedia
term can link to many adjacent articles. The project needs a durable queue so
future import runs can discover candidate sources without immediately treating
them as reviewed knowledge.

Constraints:

- The repository is public.
- Imports should remain inspectable and diffable.
- The RAG source of truth is still Markdown/JSON.
- Full-text imports may carry licensing and quality concerns.
- The queue needs to track what is discovered, what is imported, and what still
  needs review.

## Options Evaluated

### Option A: JSONDB Files in the Repository

Store import queues, term inventories, and run logs as JSON files under
`jsondb/`.

| Pros | Cons |
|------|------|
| Human-readable and diffable | Not ideal for concurrent writes |
| Works without services or dependencies | Needs validation discipline |
| Easy for the RAG to index | Large queues can become noisy |
| Matches current Markdown/JSON architecture | Querying is simpler than SQL |

### Option B: SQLite Database

Store import queue and run state in a local SQLite database.

| Pros | Cons |
|------|------|
| Better querying and transactional writes | Binary diffs are opaque |
| Handles larger queues well | Less friendly for source review |
| Easy to add indexes | Needs migration tooling |

### Option C: Issue Tracker or External Task System

Track imports as GitHub issues or another project-management system.

| Pros | Cons |
|------|------|
| Good workflow visibility | Splits source state from the KB |
| Better for human assignment | Harder for local RAG indexing |
| Rich metadata and status | Requires network and service assumptions |

## Decision

Choose Option A: JSONDB files in the repository.

This keeps the import graph close to the knowledge base, makes queue changes
reviewable in Git, and allows the local RAG to retrieve queued but unreviewed
items. SQLite can be added later if the queue grows beyond what JSON can handle
comfortably.

## Implementation Details

Added:

- `jsondb/term_inventory.json`
- `jsondb/import_queue.json`
- `jsondb/import_runs.json`
- `tools/kb_importer.py`

Queue items use `imported: false` until a source is turned into a reviewed
Markdown source card or imported Wikipedia summary card.

Wikipedia imports default to attributable summaries, not full article dumps.
Full article ingestion should remain a separate opt-in workflow because the
repository is public and Wikipedia content is CC BY-SA licensed.

