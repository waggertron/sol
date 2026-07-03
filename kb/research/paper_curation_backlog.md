# Paper Curation Backlog

## Purpose

Track the remaining paper-reference ingestion and the next curation passes for
metadata-only paper cards.

## Current Queue Shape

Snapshot after the latest metadata import runs on 2026-07-03:

- imported paper metadata cards: 1,643
- pending paper references: 286
- pending DOI-backed references: 2
- pending title-only references: 284

This means the DOI-backed backlog is effectively exhausted. What remains is a
small unresolved tail dominated by title-only references.

## Recommended Near-Term Flow

1. Promote selected metadata cards into reviewed source cards in `kb/cards/`.
2. Resolve the remaining title-only tail with a more reliable external lookup
   path or manual review.
3. Clean or manually resolve the two remaining DOI-backed records.

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

The importer now supports Crossref title-search fallback, but the remaining
title-only tail is still constrained by external lookup quality and network
behavior. The unresolved remainder should be treated as a review queue, not a
high-volume batch target.
