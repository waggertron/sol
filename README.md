# Sol

Sol is a research-first, local prototype for building a user-consented,
evidence-backed, and user-correctable personality and style model for
personalized generation.

It does **not** claim to detect a person's true personality, read minds, or
provide clinical diagnosis. Assessment results are treated as self-report
evidence, not identity facts.

> Current product thesis: authorized evidence becomes inspectable provisional
> profile atoms; users correct and scope those atoms; only eligible atoms may
> influence a specific generation task.

## Product Snapshot

The first product wedge is the **Personal Creative Style Kit**: combine
writing samples, preferences, examples, and direct calibration into an editable
style profile, then generate text and visual direction the user can evaluate.

The working implementation is currently a narrower assessment-first foundation.
It proves this local loop:

```text
consent
  -> OCEAN self-report assessment
  -> validated responses and scores
  -> provisional profile atoms
  -> evidence inspection and user correction
  -> lifecycle/scope review
  -> generation-safe context export
  -> model-free writing-guide prompt dry run
  -> structured feedback notes
```

The next product slice is a faster participant-link validation MVP: share a
no-auth link, assign an opaque participant ID, show a bounded fictional
scenario, collect the participant's organic written response, run an assessment,
generate an assessment-informed predicted response that excludes the organic
response, and ask whether the prediction sounds like the participant. The full
Style Kit guidance/source workbench follows only after this first validation
slice is interpretable.

The planned hosting path for that slice is Vercel plus hosted Postgres. Vercel
can host the public participant UI and stateless API routes, but the current
local JSONDB-backed server should not be deployed unchanged.

## What Works Today

The local assessment MVP supports:

- 11 permissive/open OCEAN and OCEAN-adjacent instruments;
- browser administration, autosave, resume, scoring, and result display;
- persisted consent plus instrument/scoring fingerprints for new sessions;
- response ID/range validation and protected completed-session evidence;
- provisional, non-diagnostic profile atoms;
- confirm, reject, review-only, claim-edit, and user-note controls;
- immutable original claims and timestamped review history;
- expandable item, keying, score, source, reliability, and uncertainty evidence;
- whole-session, raw-response-only, or derived-atom-only deletion;
- scoped profile context export with ineligible atoms excluded by default;
- a model-free writing/communication guide prompt dry run;
- structured generation feedback linked to inspectable mapping notes;
- serialized and atomic local JSONDB mutation for the single-process MVP.

The Creative Style Kit foundation now also includes five versioned record
schemas, a cross-linked example bundle, an offline validator, an ADR covering
ownership/consent/retention/deletion, and a contract-validated atomic local
repository. The repository defaults to ignored `tmp/` storage and exposes no UI
or network service yet. A guidance-domain service now enforces explicit user
review, immutable original wording, prompt-safe edit history, evidence
eligibility, and disable behavior.

Persisted pilot runs now support credential-free `dry-run://` and deterministic
`mock://` providers. Each run stores generic and personalized variants, exact
prompt-safe guidance snapshots, task/context/request hashes, provider versions,
and bounded output validation results.

Evaluation events now enforce a persisted two-step blinded lifecycle: the
opaque choice is recorded before identity reveal, and later feedback is bound
to the exact run and guidance actually used. Events are exportable and
independently deletable without changing assessment evidence or guidance.

The current automated suite has 61 tests, plus rendered desktop/mobile QA for
the Administer and Workbench views.

## What Is Not Complete

The repository does not yet provide:

- writing-sample, liked/disliked-example, or moodboard ingestion;
- browser-based contextual generation-guidance authoring;
- browser guidance, run-history, blinded comparison, and evaluation surfaces;
- participant-link scenario validation UI;
- model-backed artifact generation;
- “feels like me,” usefulness, or generic-baseline evaluation reporting;
- a validated original Sol personality assessment;
- production authentication, authorization, multi-user storage, or deployment;
- multimodal generation adapters.

Model-backed generation is intentionally unapproved until the entry conditions
in [`generation-contract-review.md`](docs/architecture/assessments/generation-contract-review.md)
are satisfied.

## Experimental Sol OCEAN Work

The repository contains one project-authored design-review candidate:

- `Sol-OCEAN-Quick-v0`
- 30 original candidate items
- five OCEAN domains
- 15 candidate subconstructs
- balanced positive/negative keying
- explicit sensitivity and expected-failure metadata

The candidate is stored at
[`assessments/ocean/experimental/sol_ocean_quick_v0.json`](assessments/ocean/experimental/sol_ocean_quick_v0.json).
It is excluded from the administrable manifest, and the product scoring/session
boundaries reject it.

Passing repository validation means the candidate is ready for independent
review—not that it is reliable, valid, normed, invariant, or product-ready.
Expert review, cognitive interviews, a pilot ADR, and empirical validation
remain required.

Validate the candidate:

```bash
python3 tools/validate_sol_ocean_candidate.py
```

## Current Repository Snapshot

As of 2026-07-12:

| Surface | Current state |
|---|---:|
| Administrable instruments | 11 |
| Stored scales | 186 |
| Stored instrument items | 1,539 |
| Experimental Sol candidates | 1 (30 items; inactive) |
| Reviewed/source cards | 15 |
| Wikipedia background cards | 1,261 |
| Paper metadata cards | 1,766 |
| Import queue records | 3,386 |
| Imported queue records | 3,089 |
| Pending paper references | 283, all title-only |
| Automated tests | 61 |

See [`docs/current-state.md`](docs/current-state.md) for the maintained handoff
and [`docs/audits/2026-07-12-initial-plan-progress-audit.md`](docs/audits/2026-07-12-initial-plan-progress-audit.md)
for the full initial-plan audit. The complete current inventory is
[`docs/inventory/2026-07-12-capability-inventory.md`](docs/inventory/2026-07-12-capability-inventory.md).

## Run The Local MVP

```bash
python3 tools/assessment_web_mvp.py --port 8765
```

Open `http://127.0.0.1:8765`.

Run automated QA:

```bash
./scripts/run_assessment_web_mvp_qa.sh
```

Capture isolated desktop/mobile visual QA:

```bash
./scripts/run_assessment_web_mvp_visual_qa.sh
```

Visual artifacts are written below ignored `tmp/assessment-web-mvp-visual/` and
do not modify tracked assessment storage.

## Model-Free Generation Dry Run

After at least one atom has confirmed/edited feedback, `active_atom` state, and
`contextual` or `global` scope:

```bash
python3 tools/generation_pilot.py \
  --pilot-id writing_guide_001 \
  --generated-at 2026-07-12T00:00:00Z
```

This renders the prompt and eligible context only. It does not call an external
model.

## Roadmap

The active product roadmap is
[`plans/14-personal-creative-style-kit-roadmap.md`](plans/14-personal-creative-style-kit-roadmap.md).

Current order:

1. Build the participant-link validation MVP in
   [`plans/16-participant-link-validation-mvp.md`](plans/16-participant-link-validation-mvp.md).
2. Add the Vercel/Postgres hosting path in
   [`plans/17-validation-mvp-hosting.md`](plans/17-validation-mvp-hosting.md).
3. Prove the predicted response uses assessment-derived candidate context while
   excluding the participant's organic response.
4. Store alignment/misalignment feedback as evaluation evidence, not as an
   automatic rewrite of assessment claims or confidence.
5. Run a small consenting pilot and decide whether the output sounds like users.
6. Expand into fuller Style Kit guidance, source intake, visual inputs, or
   platform extraction only after the validation gate is reviewed.

Independent expert/cognitive review of the experimental Sol OCEAN candidate is
a parallel validation track, not a dependency of the product wedge.

Detailed ledgers:

- [`plans/11-mvp-hardening-and-profile-loop.md`](plans/11-mvp-hardening-and-profile-loop.md)
- [`plans/12-post-audit-roadmap.md`](plans/12-post-audit-roadmap.md)
- [`plans/13-sol-ocean-experimental-assessment.md`](plans/13-sol-ocean-experimental-assessment.md)
- [`plans/14-personal-creative-style-kit-roadmap.md`](plans/14-personal-creative-style-kit-roadmap.md)
- [`plans/15-style-kit-validated-execution.md`](plans/15-style-kit-validated-execution.md)
- [`plans/16-participant-link-validation-mvp.md`](plans/16-participant-link-validation-mvp.md)
- [`plans/17-validation-mvp-hosting.md`](plans/17-validation-mvp-hosting.md)

## Safety Boundaries

Blocked by default:

- clinical diagnosis or personality-disorder labeling;
- protected-class inference;
- hidden profiling;
- covert political persuasion;
- employment, housing, lending, insurance, legal, or education eligibility use.

High-sensitivity claims—such as trauma interpretation, emotional instability,
honesty/exploitiveness, attachment, intelligence, or competence—must not be
casually inferred or used as ordinary generation controls.

## Research And Knowledge Base

The repository includes reviewed source cards, metadata-only paper imports,
Wikipedia background summaries, model contracts, assessment catalogs, and a
local lexical RAG index.

Build the index:

```bash
python3 tools/rag.py index
```

Search or print context:

```bash
python3 tools/rag.py search "construct validity personality profile"
python3 tools/rag.py context "why broad traits should not control generation" --top-k 6
```

Metadata imports are background references, not reviewed knowledge. Research
changes reach product behavior only through reviewed cards, model/contract
updates, and ADRs where appropriate.

## Repository Map

- `app/assessment-mvp/` — local browser UI.
- `assessments/ocean/instruments/` — administrable permissive/open instruments.
- `assessments/ocean/experimental/` — inactive project-authored candidates.
- `kb/cards/` — reviewed research source cards.
- `kb/model/` — knowledge, signal, and profile-atom contracts.
- `kb/assessments/` — assessment catalogs, mappings, and construct blueprints.
- `docs/architecture/` — implementation and research architecture.
- `docs/adr/` — architecture decisions.
- `docs/audits/` — repository plan/progress audits.
- `plans/` — committed product and research execution ledgers.
- `jsondb/` — local queues and MVP persistence.
- `tools/` — RAG, import, assessment, validation, and pilot CLIs.
- `.codex/skills/` — repo-local reusable agent workflows.

## Key Documents

- [`docs/project-memory.md`](docs/project-memory.md)
- [`docs/current-state.md`](docs/current-state.md)
- [`kb/model/profile_atom_schema_v0.md`](kb/model/profile_atom_schema_v0.md)
- [`docs/architecture/assessments/web-mvp.md`](docs/architecture/assessments/web-mvp.md)
- [`docs/architecture/assessments/sol-ocean-experimental.md`](docs/architecture/assessments/sol-ocean-experimental.md)
- [`docs/adr/2026-07-12-style-kit-record-contracts.md`](docs/adr/2026-07-12-style-kit-record-contracts.md)
- [`docs/adr/2026-07-13-participant-link-validation-mvp.md`](docs/adr/2026-07-13-participant-link-validation-mvp.md)
- [`docs/adr/2026-07-13-vercel-validation-mvp-hosting.md`](docs/adr/2026-07-13-vercel-validation-mvp-hosting.md)
- [`docs/architecture/rag/research-promotion-workflow.md`](docs/architecture/rag/research-promotion-workflow.md)
