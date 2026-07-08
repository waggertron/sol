# Paper Tail Curation Plan

## Objective

Finish the current paper-reference backlog in a controlled way now that the
DOI-backed queue is exhausted and the remainder is mostly title-only.

This plan treats the remaining queue as a curation and selective-resolution
problem, not a blind batch-ingestion problem.

## Current State

Snapshot aligned to `docs/current-state.md` on 2026-07-06:

- pending paper references: 283
- pending DOI-backed references: 0
- pending title-only references: 283
- rejected records: 21
- deferred records: 31
- manual mappings: 2
- unreviewed records: 231

Primary operating artifacts:

- `jsondb/paper_import_review.json`
- `jsondb/import_queue.json`
- `kb/research/paper_review_queue.md`
- `kb/paper_imports/`

## Problem Shape

The queue now mixes four distinct cases:

1. obvious non-article references
2. journal-title-only or series-title-only noise
3. real works that may still be resolvable as papers or chapters
4. ambiguous short or generic titles with high false-match risk

The first two categories should be removed from the active retry path through
review decisions. The third category is where new metadata-card yield remains.
The fourth category should be handled carefully and may remain unresolved.

## Operating Principle

Prefer precision over throughput.

Do not push items through Crossref title search unless the expected value is
higher than the risk of bad matches and timeout churn.

## Phases

### Phase A: Conservative Queue Hygiene

Goal:

- keep shrinking the backlog by removing obvious non-article items

Allowed actions:

- `rejected_items` for journal-title-only or series-title-only records
- `deferred_items` for books, handbooks, edited volumes, reference works,
  websites, news citations, and in-press items

Do not:

- reject or defer items that plausibly look like standalone journal articles
- use broad heuristics on short or generic titles without inspection

Batch size:

- 5 to 12 items per pass

Stop condition:

- a scan of the next 40 to 60 unreviewed items yields fewer than 3
  low-ambiguity defer/reject decisions

### Phase B: Clustered Manual Resolution

Goal:

- resolve the highest-value remaining items into metadata cards

Suggested cluster order:

1. personality theory and trait theory
2. developmental personality and life-course work
3. psychometrics and assessment theory
4. digital-trace / social-data methodology

Resolution methods:

- manual DOI mapping into `paper_import_review.json`
- manual non-Crossref source mapping for OSF-like or atypical sources
- selective `import-paper-manual-matches`

Batch size:

- 10 to 20 items from one domain cluster at a time

Stop condition:

- fewer than 20 percent of the inspected batch resolves cleanly

### Phase C: Importer Reassessment

Goal:

- decide whether more automation work is justified

Only consider importer changes if the remaining queue still contains a large
number of likely-resolvable articles or chapters.

Possible improvements:

- venue-aware title scoring
- chapter/book-pattern detection before Crossref
- abbreviation handling for journals
- curated exporter for likely-manual-match candidates

Do not build this phase by default. Use it only if Phase B reveals repeated,
structured resolution patterns.

## Success Metrics

Primary:

- keep false positive imports near zero
- reduce active unreviewed queue count
- increase the share of queue records with explicit review state

Secondary:

- add high-value metadata cards
- reduce repeated timeout churn in `import-paper-metadata`

## Operational Commands

Review application:

```bash
python3 tools/kb_importer.py apply-paper-review
```

Manual-match import only:

```bash
python3 tools/kb_importer.py import-paper-manual-matches --sleep 0
```

Review queue regeneration:

```bash
python3 tools/kb_importer.py paper-review-report --limit 200 --output kb/research/paper_review_queue.md
```

Use `import-paper-metadata` only in narrow, intentional batches after a manual
selection step.

## Near-Term Execution Order

1. Continue Phase A until obvious defer/reject opportunities thin out.
2. Start Phase B with the 2003-2009 personality-theory cluster.
3. Re-evaluate whether the remaining queue justifies Phase C.

## Current Recommendation

The next working session should remain in Phase A/Phase B transition:

- finish the easy curation wins
- then move to slower, cluster-based manual resolution

This is the highest-signal path from the current state.
