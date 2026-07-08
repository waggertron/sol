# Paper Curation Backlog

## Purpose

Track the remaining paper-reference ingestion and the next curation passes for
metadata-only paper cards.

## Current Queue Shape

Snapshot after the latest metadata import runs on 2026-07-06:

- imported paper metadata cards: 1,646
- pending paper references: 283
- pending DOI-backed references: 0
- pending title-only references: 283
- seeded review rejections: 21
- seeded review deferrals: 31
- seeded manual mappings: 2

This means the DOI-backed backlog is now exhausted. What remains is a small
unresolved tail composed entirely of title-only references.

## Recommended Near-Term Flow

1. Promote selected metadata cards into reviewed source cards in `kb/cards/`.
2. Curate unresolved titles through `jsondb/paper_import_review.json` and
   `kb/research/paper_review_queue.md`.
3. Continue conservative book/chapter/volume triage on the remaining title-only
   queue.

## Promotion Heuristics

Use these fields to choose which metadata-only cards to read and promote first:

- direct relevance to the knowledge model or first MVP
- foundational status in trait theory, psychometrics, language inference, or
  clinical boundary-setting
- high Crossref cited-by count
- repeated appearance across adjacent-source chains
- clear usefulness for product constraints, assessment design, or profile atom
  modeling

## Current Constraint

The importer now supports Crossref title-search fallback, stricter title-match
scoring, and a persisted review DB. The remaining title-only tail is still
constrained by external lookup quality, old book/chapter citations, and
network behavior. The unresolved remainder should be treated as a review queue,
not a high-volume batch target.

The seeded review passes have already removed obvious churn cases:

- reject journal-title-only and series-title-only queue records
- defer books, manuals, edited volumes, and in-press citations for manual
  handling
- manually resolve nonstandard DOI cases before they churn through retry loops

Recent note: a follow-on small title-resolution batch still stalled on Crossref
title-search timeouts before importing additional records, so curation remains
the higher-yield next step for this tail.

## Review Workflow

Use these artifacts together:

- `jsondb/paper_import_review.json` for persisted defer/reject/manual DOI
  decisions
- `kb/research/paper_review_queue.md` for the current unresolved-paper queue
- `python3 tools/kb_importer.py apply-paper-review` to push defer/reject notes
  into queue state
- `python3 tools/kb_importer.py paper-review-report` to regenerate the Markdown
  review queue after updates
