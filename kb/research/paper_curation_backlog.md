# Paper Curation Backlog

## Purpose

Track the remaining paper-reference ingestion and the next curation passes for
metadata-only paper cards.

## Current Queue Shape

Snapshot after the latest metadata import run on 2026-07-03:

- imported paper metadata cards: 1,125
- pending paper references: 804
- pending DOI-backed references: 506
- pending title-only references: 298

This means the next large automated batch can continue on DOI-backed Crossref
imports, while the title-only remainder needs a separate resolution workflow.

## Recommended Near-Term Flow

1. Continue bounded `import-paper-metadata` batches against DOI-backed items.
2. Periodically rebuild the RAG index after each large batch.
3. Promote selected metadata cards into reviewed source cards in `kb/cards/`.
4. Add a dedicated title-resolution path for `paper-title:*` queue items.

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

The importer can only automate queue items that already have DOIs. The
title-only backlog now represents the main curation gap in the paper pipeline.
