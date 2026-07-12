# Project Memory

This is the compact context to preserve across future planning and development
sessions.

## Project Intent

Build a platform for user-consented personality and style modeling. The system
should infer evidence-weighted, user-correctable profile atoms from authorized
data, then use those atoms to personalize generated outputs across modalities.

Do not frame the system as a true personality detector, mind reader, diagnostic
engine, or literal neuroscience engram.

Preferred framing:

> an evidence-backed, user-correctable personality and style model for
> personalized multimodal generation

## Initial Product Strategy

The long-term product is a platform, but the first implementation should be a
single wedge that exercises the complete loop.

Current recommended wedge:

> Personal Creative Style Kit

The wedge should begin with user-provided writing samples, preferences,
examples, and direct calibration answers; produce an editable style profile;
then generate text the user can compare with a generic baseline. Visual
direction comes only after the text loop demonstrates value.

Direct style choices and authorized writing evidence are the primary product
signals. OCEAN assessment is optional context, not required onboarding and not
a direct global generation control.

## Core Loop

1. User authorizes or provides data.
2. System extracts observations with source provenance.
3. Observations become provisional profile atoms.
4. User confirms, edits, rejects, or scopes those atoms.
5. Generation uses confirmed or high-confidence atoms.
6. Output feedback updates scoped generation guidance or records a correction;
   it does not silently rewrite assessment evidence or confidence.

## Research Principles

- Use rigorous psychology, psychometrics, linguistics, behavioral science,
  abnormal psychology, HCI, and computational social science.
- Keep observed data, style preference, trait hypothesis, and sensitive
  hypothesis separate.
- Prefer context-aware if-then patterns over global personality labels.
- Treat broad trait models as organizing layers, not direct generation controls.
- Use clinical and abnormal psychology mainly for boundary-setting.
- Store confidence, counterevidence, context, recency, and user confirmation.

## Current Knowledge Base Shape

- `kb/00_intent.md` defines project intent and boundaries.
- `kb/model/knowledge_model_v0.md` defines the first research ontology.
- `kb/model/signal_matrix_v0.md` maps data sources to permissible inference
  levels.
- `kb/cards/` contains source cards.
- `kb/assessments/` contains OCEAN assessment catalog and profile atom mapping
  notes.
- `sources/sources.json` tracks source metadata.
- `sources/adjacent_sources_v1.json` tracks 34 adjacent research sources.
- `jsondb/import_queue.json` tracks 3,386 pending/imported/rejected research
  import candidates.
- `jsondb/paper_import_review.json` stores manual defer/reject/manual-DOI
  decisions for unresolved paper references.
- `kb/wiki_imports/` contains 1,261 background Wikipedia summary imports.
- `kb/paper_imports/` contains 1,766 metadata-only paper imports from queued DOI
  references.
- `kb/research/paper_review_queue.md` is the generated manual-review queue for
  unresolved paper references.
- `assessments/ocean/` stores the current OCEAN assessment corpus: 11
  instruments, 186 scales, and 1,539 items.
- `tools/rag.py` provides local lexical retrieval.
- `tools/kb_importer.py` manages research import queues.
- `tools/kb_importer.py import-queued-wikipedia` imports pending linked
  Wikipedia summaries; `import-paper-metadata` imports Crossref metadata-only
  cards for queued DOI references; `import-paper-manual-matches` imports only
  manually curated paper mappings.
- `tools/assessment_to_profile_atoms.py` is the first implementation-facing
  assessment generator. It loads stored instrument JSON, scores responses, and
  emits `profile_atom_schema_v0`-aligned `provisional_atom` records.
- `tools/assessment_session_store.py` is the first local persistence layer for
  assessment sessions. It stores raw responses separately from derived scores
  and derived atoms in `jsondb/assessment_sessions.json`.
- `tools/run_assessment_mvp.py` is the first end-to-end MVP runner. It creates
  a local session, stores responses, scores the instrument, derives
  `provisional_atom` candidates, and writes export artifacts under
  `artifacts/assessment_runs/`.
- `tools/assessment_web_mvp.py` is the first local browser-facing assessment
  surface. It serves a static UI plus a thin JSON API over the same shared
  session-store contract. It now supports session export/delete and a
  cross-session profile atom workbench.
- The profile workbench supports session-scoped claim edits and user notes
  while retaining immutable generated wording in `original_claim` and material
  changes in append-only `review_history`.
- Assessment score and atom views expose raw/normalized score context,
  item-level response and keying calculations, instrument provenance, and
  uncertainty cautions. Reliability is framed as consistency evidence rather
  than proof of an individual claim.
- `build_profile_context` and `GET /api/profile-context` provide the first
  generation-facing packet. Default selection is confirmed/edited active
  contextual/global atoms with non-blocked sensitivity; rejected/suppressed
  atoms are excluded, and explicitly included review-only atoms remain
  generation-ineligible.
- `tools/generation_pilot.py` renders the first model-free writing and
  communication guide prompt using only generation-eligible packet atoms.
  Optional artifacts are restricted to ignored `tmp/generation-pilot/` paths.
- Generation feedback is stored as explicit evaluation events and appended to
  atom `generation_mapping_notes` with provenance. It does not silently alter
  raw assessment data, claims, or confidence.
- The 2026-07-11 generation contract review did not approve model-backed mode.
  The next prerequisites are user-reviewed generation mappings and persisted
  pilot-run provenance; see
  `docs/architecture/assessments/generation-contract-review.md`.
- The 2026-07-12 integrity pass moved validation, persisted consent/version
  provenance, lifecycle invariants, atomic mutation, rescore protection, and
  selective deletion into the shared assessment session-store boundary.
- Original Sol OCEAN Phase 3 now has a design-review blueprint at
  `kb/assessments/sol_ocean_construct_blueprint_v0.md` and a 30-item candidate
  at `assessments/ocean/experimental/sol_ocean_quick_v0.json`. It is excluded
  from the manifest and must not emit product atoms before expert review,
  cognitive interviews, a pilot ADR, and later empirical validation.
- The reusable workflow for future project-authored assessment candidates lives
  at `.codex/skills/sol-experimental-assessment-workflow/SKILL.md`. The durable
  lesson is that structural completeness, scoring metadata, and passing tests
  are readiness for review—not psychometric validation or product activation.
- The complete 2026-07-12 repository inventory lives at
  `docs/inventory/2026-07-12-capability-inventory.md`. The active product roadmap
  is `plans/14-personal-creative-style-kit-roadmap.md`: prove a consented
  writing-evidence and direct-preference loop locally, compare personalized and
  generic outputs, and keep real-model, visual, and platform expansion behind
  explicit evidence and safety gates.
- Creative Style Kit Phase 0 is fixed by
  `docs/adr/2026-07-12-style-kit-record-contracts.md` and the five schemas below
  `schemas/style_kit/v1/`. The v1 policy is self-authored writing only,
  local-until-deleted retention, independent cross-linked records, and no
  external provider. `plans/15-style-kit-validated-execution.md` is the active
  small-increment ledger. Increment 1 added an atomic, contract-validating,
  filesystem-backed repository at `tools/style_kit_store.py`. Increment 2 added
  explicit user-reviewed guidance lifecycle at `tools/style_kit_guidance.py`
  and centralized atom eligibility in `tools/profile_atom_policy.py`. Increment
  3 added persisted dry-run/mock generic-personalized run pairs, exact
  prompt-safe guidance snapshots, deterministic request/context hashes, and
  bounded output validation at `tools/style_kit_pilot.py`. Increment 4 added the
  two-step blinded lifecycle at `tools/style_kit_evaluation.py`, bound to exact
  completed mock runs and used guidance, with independently deletable feedback.
  The recorded stopping point is after Increment 4; Increment 5 browser
  workbench work is explicitly unstarted.
- Wikimedia/Wikipedia imports must be slow and serial: default to `--sleep 12`,
  keep queue-drain runs at `--link-limit 0`, do not run parallel jobs, and stop
  after HTTP `429` or `503` once `Retry-After` or the configured delay has been
  respected. Wikipedia import commands emit progress logs by default; use
  `--no-progress` only for quiet JSON-only runs. Queue imports checkpoint after
  each attempted item. Current state: all `wikipedia_article` queue records are
  imported; the remaining Wikipedia backlog is a small review tail rather than
  a large blind batch target.
- Paper ingestion now includes Crossref title-search fallback in addition to
  DOI lookups. It now also includes stricter title-match scoring plus a
  persisted review DB for defer/reject/manual DOI resolution. That cleared most
  of the backlog, and the remaining unresolved tail is now entirely
  `paper-title:*` records that should be handled as a review queue rather than
  a blind bulk batch. The two DOI-backed failures are now resolved through
  manual mapping. Current seeded review state: 21 rejected
  journal-title-only or series-title-only records, 31 deferred
  book/manual/in-press or volume records, and 14 manual mappings (including the
  two mappings that resolved the former DOI-backed failures and later curated
  cluster imports).
- The operating plan for the remaining paper tail now lives in
  `plans/09-paper-tail-curation.md`. Default approach: conservative hygiene
  passes first, then clustered manual resolution, and only then reconsider
  importer automation.
- A reviewed consciousness/workspace cluster is now present in
  `kb/cards/baars_global_workspace_theory.md` and
  `kb/cards/dehaene_workspace_neuroscience.md`. These sources are being used
  only for architecture around salience, thresholding, and candidate-vs-active
  profile atoms, not for neuroscientific claims about users.
- The repo now has a durable research-promotion workflow in
  `docs/architecture/rag/research-promotion-workflow.md` and a local reusable
  workspace skill at `.codex/skills/sol-research-kb-workflow/SKILL.md` for
  future paper-cluster ingestion and promotion work.
- Repo-local agent guidance now lives in:
  `AGENTS.md`, `assessments/AGENTS.md`, and `kb/AGENTS.md`.
- `tools/import_ocean_assessments.py` normalizes downloaded official assessment
  pages into repo JSON.
- `docs/architecture/assessments/profile-atom-output.md` defines the current
  scoring-to-profile-atom output contract.
- `docs/architecture/assessments/session-storage.md` defines the current local
  assessment session persistence contract.
- `docs/architecture/assessments/mvp-flow.md` defines the current executable
  MVP assessment flow.
- `docs/architecture/assessments/web-mvp.md` defines the current browser-based
  assessment surface and route contract.

The latest snapshot is maintained in `docs/current-state.md`.

## Current Build Direction

The assessment administration foundation is complete enough for the next
product proof. Build the Creative Style Kit text loop in this order:

1. Add browser guidance, run-history, comparison, and evaluation surfaces.
2. Add consented writing samples and direct style calibration.
3. Present source-bound observations and editable contextual guidance.
4. Compare personalized and generic text artifacts blind and bind feedback to
   the exact run and guidance used.
5. Validate export, cascading deletion, and ineligible-atom exclusion.
6. Use the product-value gate before any real model, visual input, or platform
   extraction.

## Key Source Anchors

- Frontiers 2022 paper that inspired the project: trait-context-behavior-output
  layering.
- Big Five and HEXACO: broad trait structure.
- CAPS and Whole Trait Theory: context, dynamics, if-then signatures, and
  state distributions.
- Cronbach and Meehl: construct validity and nomological networks.
- Schwartz et al. and Youyou et al.: language and digital footprint inference.
- ICD-11, HiTOP, RDoC: clinical boundary awareness, not product diagnosis.

## Hard Boundaries

Default blocked:

- clinical diagnosis
- personality disorder labeling
- protected class inference
- covert political persuasion
- hidden profiling
- employment, housing, lending, insurance, legal, or education eligibility use

Default high-sensitivity:

- trauma interpretations
- maladaptive personality extremes
- honesty/exploitiveness claims
- emotional instability claims
- attachment-style claims
- intelligence or competence claims
