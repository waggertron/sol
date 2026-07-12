# Initial Plan And Progress Audit

Audit date: 2026-07-12

## Executive Summary

Sol has built a credible research and assessment-first foundation, but it has
not yet delivered the original Personal Creative Style Kit wedge.

The strongest completed path is:

```text
stored OCEAN instrument
  -> local consent checkbox
  -> response session
  -> scored self-report evidence
  -> provisional profile atoms
  -> inspect/edit/confirm/reject
  -> scoped context export
  -> model-free writing-guide prompt dry run
  -> structured feedback notes
```

This is meaningful progress: it proves most of the assessment-to-profile loop,
has explicit safety boundaries, and has a repeatable local QA baseline. The
original wedge, however, also called for writing samples, preference examples,
creative/aesthetic inputs, a profile spanning more than broad OCEAN traits,
and generated text/visual artifacts that users can compare and rate. Those
parts remain largely unimplemented.

The audit also found several implementation defects or contract gaps that
should be repaired before expanding the product surface. The highest-priority
confirmed defect is unreachable item-count confidence logic in the assessment
scorer. Other high-priority gaps concern response validation, rescoring after
user review, persisted consent/version provenance, JSONDB mutation safety, and
deletion semantics.

## Scope And Method

This audit compares the repository against:

- `plans/00-plan-of-plans.md`
- `plans/01-product-vision.md` through `plans/08-ocean-assessment-plan.md`
- `plans/09-paper-tail-curation.md`
- `plans/10-assessment-web-mvp-implementation.md`
- `plans/11-mvp-hardening-and-profile-loop.md`
- `docs/project-memory.md`
- `docs/current-state.md`

Implementation evidence was inspected in `app/`, `tools/`, `tests/`, `kb/`,
`assessments/`, and `jsondb/`. The repository QA suite was run without changing
tracked assessment storage.

This is not a scientific validation of the assessments or a security audit of a
deployed service. The current app is local-only and has no production auth,
multi-user isolation, or deployment boundary to assess.

## Current Evidence Snapshot

### Repository And Validation

- Branch: `main`, synchronized with `origin/main` at audit start.
- Automated QA after remediation: 20 tests pass.
- QA invariant: tracked `jsondb/assessment_sessions.json` remains unchanged.
- Rendered QA baseline exists for desktop/mobile Administer and Workbench views.
- Current tracked sessions: 2 completed sample sessions, 10 scores, 10 atoms.
- Current tracked generation feedback events: 0.

### Research And Assessment Corpus

Measured on 2026-07-12:

| Surface | Measured | Previously documented |
|---|---:|---:|
| RAG index file | 23 MB | 20,600 chunks |
| Reviewed/source cards in `kb/cards/` | 15 Markdown files | 13 source cards |
| Wikipedia background cards | 1,261 | 1,261 |
| Paper metadata cards | 1,766 | 1,646 |
| Import queue records | 3,386 | 3,373 |
| Imported queue records | 3,089 | 3,076 |
| Pending queue records | 297 | not stated as a total |
| Paper review rejections | 21 | 21 |
| Paper review deferrals | 31 | 31 |
| Paper manual mappings | 14 | 2 |
| Stored OCEAN instruments | 11 | 11 |
| Stored scales | 186 | 186 |
| Stored items | 1,539 | 1,539 |

The corpus is larger than `docs/current-state.md` reports. The document is not
unsafe, but it is stale and should not be treated as an exact operational
snapshot until refreshed.

## Original Plan Progress Matrix

Status meanings:

- **Complete**: implemented and supported by repository evidence.
- **Partial**: a meaningful slice exists, but the planned outcome is incomplete.
- **Planned only**: described in plans/docs without a working implementation.
- **Deferred by design**: intentionally blocked pending safety or contract work.

| Plan area | Status | What exists | What remains |
|---|---|---|---|
| Product vision | Partial | Clear thesis, boundaries, target-user hypotheses, local assessment wedge | Initial target segment is still unresolved; no user validation of creator vs productivity vs reflection positioning |
| Personal Creative Style Kit | Partial | Editable assessment-derived profile cards, scoped context, writing-guide dry run | Writing samples, liked/disliked examples, moodboards, aesthetic profile, text/visual artifacts, comparative ratings |
| Knowledge model | Partial/strong | Ontology, signal matrix, profile atom lifecycle/schema, provenance, context, confidence, counterevidence, review history | Machine-readable schema, calibrated confidence across sources, generation-guidance authoring, non-assessment observations |
| Data and consent | Partial/weak | Client-side consent checkbox, session export/delete, visible evidence and corrections | Persisted consent receipt, source-level permissions, separate raw/derived deletion, retention policy, third-party-data policy |
| RAG research | Partial/strong | Large lexical index, import queues, metadata cards, 15 reviewed cards, promotion workflow | Remaining paper curation, evidence coverage beyond a small reviewed-card set, retrieval evaluation, stale corpus reporting |
| Platform architecture | Partial | Thin local API, shared scoring/session store, scoped context builder, feedback events | Real consent/profile services, durable datastore, concurrency/migrations, ingestion/extraction, persisted pilot runs, generation provider boundary |
| Evaluation and safety | Partial | Blocked-use policy, non-diagnostic copy, eligibility filtering, prompt review gate, correction controls | “Feels like me” measurement, generic-vs-personalized comparison, correction/rejection analytics, calibration study, user-study protocol execution |
| OCEAN research | Partial | Broad corpus and assessment catalog | Domain-by-domain reviewed definitions/cautions and primary-source coverage are not demonstrated as complete |
| OCEAN assessment acquisition | Complete for prototype | 11 stored instruments with license posture; proprietary/reference-only inventory | Ongoing license review and validation-source curation |
| Original Sol assessment design | Planned only | Candidate names and methodology in Plan 08 | No reviewed construct blueprint, original item pool, scoring spec, or empirical validation |
| Assessment web MVP | Complete for local prototype | Catalog, consent gate, questionnaire, autosave/resume, scoring, results, atom review, export/delete, workbench | Persisted consent/version proof, admin scoring/version view, selective deletion, production concerns |
| MVP hardening phases 1-4 | Complete with defects noted below | QA, atom editing/history, evidence views, scoped export | Correctness and storage hardening findings from this audit |
| First generation pilot | Partial/deferred | Safe dry-run prompt, scoped eligible context, structured feedback contract | User-authored mappings, persisted pilot run, actual artifact, output validation, provider opt-in; model mode correctly unapproved |
| Multimodal expansion | Planned only | Product and ontology language anticipates it | No image/audio/video ingestion or generation adapters |

## What Has Been Achieved

### 1. Research-First Safety Posture

The repository consistently avoids diagnostic or mind-reading framing. Broad
trait claims begin as provisional self-report evidence, are user-visible, and
default to `review_only`. Sensitive and blocked-use boundaries appear in the
model, plans, UI copy, and generation packet.

### 2. A Real Assessment Administration Slice

The browser app can load stored instruments, collect responses, autosave,
resume, score, display results, and derive profile atoms. TIPI and Mini-IPIP
have focused evidence tests, and all 11 stored instruments use one of the two
implemented scoring methods.

### 3. User-Correctable Profile Atoms

The profile workbench supports confirmation, rejection, review-only state,
claim editing, and notes. `original_claim` and append-only `review_history`
preserve the generated starting point and material changes.

### 4. Explainability And Scoped Export

Score and atom views expose item responses, keying direction, reverse scoring,
instrument/source context, reliability cautions, and TIPI precision warnings.
The scoped packet excludes rejected, suppressed, unconfirmed, review-only, and
blocked-sensitivity atoms from generation eligibility by default.

### 5. A Responsible Generation Gate

The dry run separates system instructions from structured profile data, treats
embedded claim text as data rather than instructions, and never calls an
external model. The generation contract review explicitly declined to approve
model-backed execution until additional provenance and authoring conditions are
met.

## Confirmed Findings

### Remediation Status

The audit was followed immediately by an integrity repair pass. Status below
reflects the post-repair worktree and the 20-test validation run.

| Finding | Status | Resolution |
|---|---|---|
| F1 confidence fallback | Resolved | Item-count branches restored with 2/4/8+ boundary tests |
| F2 response validation | Resolved | Shared store rejects unknown IDs and values outside the instrument scale |
| F3 rescore overwrite | Resolved | Completed responses are immutable and reviewed atoms cannot be overwritten by rescoring |
| F4 JSONDB mutation safety | Resolved for single process | Reentrant mutation lock plus atomic same-directory file replacement |
| F5 consent/version provenance | Resolved for new sessions | Consent receipt, schema version, scoring method, and instrument SHA-256 stored and verified |
| F6 deletion semantics | Resolved | Separate raw-response and derived-atom deletion plus feedback-reference cleanup |
| F7 lifecycle combinations | Resolved | Shared invariant validation rejects incompatible state/scope/feedback combinations |
| F8 persisted pilot runs | Open | Required before model-backed generation |
| F9 guidance authoring | Open | Required before model-backed generation |
| F10 operational evaluation | Open | Required to validate product usefulness |
| F11 stale state counts | Resolved | Current-state counts refreshed from repository data |
| F12 original wedge inputs | Open | Planned return after integrity and generation-contract work |

### High Impact

#### F1. Item-count confidence fallback is unreachable

- Type: Correctness
- Confidence: High
- Evidence: `tools/assessment_to_profile_atoms.py:89-119`

`confidence_for_scale` returns `0.58` whenever reliability alpha is absent.
The intended item-count branches were accidentally placed after the final
return in `uncertainty_note`, making them unreachable. Brief TIPI scales and
longer scales without alpha therefore receive the same fallback confidence.

Impact: stored confidence is inconsistent with the documented and apparently
intended policy; current tests do not catch the TIPI fallback regression.

Required fix: restore the item-count branches inside `confidence_for_scale` and
add boundary tests for 2, 4, and 8+ items.

Resolution: implemented in the 2026-07-12 integrity repair pass.

#### F2. Response IDs and values are not validated before persistence/scoring

- Type: Correctness / contract safety
- Confidence: High
- Evidence: `tools/assessment_session_store.py:293-306` and
  `tools/assessment_to_profile_atoms.py:129-168`

Responses are converted to floats but not checked against the selected
instrument’s item IDs or response-scale values. Unknown keys can be stored, and
out-of-range values can produce out-of-range scores and misleading claims.

Impact: the core assessment contract can accept invalid evidence while still
presenting a polished result.

Required fix: validate IDs and allowed numeric values at the shared session
store boundary; keep explicit negative fixtures separate from valid fixtures.

Resolution: implemented in the shared store with explicit invalid-ID and
out-of-range fixtures.

#### F3. Rescoring replaces reviewed atoms

- Type: Correctness / user-data preservation
- Confidence: High
- Evidence: `tools/assessment_session_store.py:315-329`

`score_session` replaces the entire `profile_atoms` list. If a completed
session is scored again after atom confirmation, edits, notes, or generation
feedback, those review artifacts are lost.

Impact: user corrections and provenance can be silently destroyed.

Required fix: define a rescore policy. The safest near-term option is to block
response mutation/rescoring after review and require a new session, or implement
an explicit versioned re-derivation history rather than an implicit merge.

Resolution: completed-session responses are immutable, and rescoring is refused
once atoms carry review or generation-feedback state.

#### F4. JSONDB mutations are not atomic or serialized

- Type: Correctness / architecture
- Confidence: High
- Evidence: `tools/assessment_session_store.py:35-60` and use of
  `ThreadingHTTPServer` in `tools/assessment_web_mvp.py`

Every mutation performs an unlocked read-modify-write of one JSON file. The web
server is threaded, so overlapping autosave, score, review, feedback, or delete
requests can lose updates. Direct writes also risk a partial file if interrupted.

Impact: the local MVP can corrupt or overwrite session state under legitimate
concurrent requests.

Required fix: add an in-process mutation lock and atomic temporary-file replace;
document that this remains single-process only.

Resolution: implemented and documented as single-process integrity, not a
production transaction model.

#### F5. Consent and assessment-version provenance are claimed more strongly than stored

- Type: Missing contract
- Confidence: High
- Evidence: client-only check at `app/assessment-mvp/app.js:502-513`; session
  shape at `tools/assessment_session_store.py:264-287`

The consent checkbox is not persisted. Sessions store instrument ID/name/path,
but no consent timestamp/version, instrument schema version, scoring-contract
version, or content hash. `docs/current-state.md` says scores are stored with
instrument-version provenance, which is not fully supported by the stored shape.

Impact: the system cannot later prove which consent language or exact scoring
definition governed a result.

Required fix: persist a consent receipt and immutable instrument/scoring
fingerprint at session creation.

Resolution: new sessions persist consent version/time/scope, instrument schema
version, scoring method, and SHA-256; the fingerprint is checked before response
mutation or scoring. Historical sessions remain readable without fabricated
receipts.

#### F6. Deletion semantics do not meet the initial consent plan

- Type: Privacy / missing feature
- Confidence: High
- Evidence: `plans/04-data-consent.md:23-27` versus
  `tools/assessment_session_store.py:341-348`

Only whole-session deletion exists. Users cannot separately delete raw
responses or derived atoms as originally required. Deleting a session also does
not reconcile root-level `generation_feedback` events that reference its atoms.

Impact: data control is weaker than the plan and can leave orphan provenance.

Required fix: define selective deletion/tombstone behavior and cascade or redact
feedback references consistently.

Resolution: the CLI/API/workbench can delete responses or atoms separately;
atom/session deletion cleans or removes linked feedback events.

### Medium Impact

#### F7. Lifecycle transitions can form inconsistent states

`review_atom` validates enum membership but not combinations. API/CLI callers
can create `active_atom + review_only`, `suppressed_atom + confirmed`, or active
but unconfirmed states. Generation eligibility now filters these defensively,
but the stored profile can still be internally inconsistent.

Recommendation: centralize allowed transitions and state/scope/feedback
invariants, then use the same validator in UI, CLI, API, and packet export.

#### F8. Generation feedback is not tied to a persisted pilot run

Feedback accepts a bounded `pilot_id`, but dry runs are not registered in the
session store. A caller can submit feedback for an arbitrary pilot ID or atoms
that were eligible generally but were not necessarily used in that run.

Recommendation: persist pilot records containing prompt version, exact atom
references, context hash, timestamps, mode, and eventual output metadata; only
accept feedback against that record.

#### F9. Generation guidance has no user authoring path

Assessment-derived atoms initialize `generation_mappings` as empty. The prompt
correctly refuses to invent guidance, so the current dry run can mostly produce
confirmation questions rather than a meaningful style guide.

Recommendation: add explicit, contextual, user-reviewed generation guidance
before model-backed generation.

#### F10. Evaluation is designed but not operationalized

The plans name “feels like me,” usefulness, correction rate, rejection rate,
generic-vs-personalized preference, and confidence calibration. Only categorical
pilot feedback is stored; there is no evaluation protocol execution or metric
reporting.

Recommendation: implement a small local evaluation event schema and baseline
comparison before expanding modalities.

#### F11. Current-state counts and handoff commits are stale

`docs/current-state.md` undercounts source cards, paper imports, queue records,
and manual mappings. Its “latest committed” visual/task-ledger hashes also
predate several completed phases.

Recommendation: generate or verify counts through a read-only status command
and refresh the handoff after correctness fixes.

#### F12. The original wedge inputs remain absent

No implementation ingests writing samples, preference examples, direct
calibration beyond assessment answers, or visual references. This is the main
product gap between the assessment MVP and the Personal Creative Style Kit.

Recommendation: after the correctness/privacy hardening pass, choose one
non-assessment source—preferably writing samples plus direct style ratings—and
carry it through the same observation/provisional/review lifecycle.

### Lower Impact / Expected MVP Limits

- The local web app has no authentication or multi-user authorization.
- JSONDB has no schema migration framework.
- Instrument paths are local filesystem references rather than immutable
  registry records.
- Rendered QA captures screenshots but does not automate expanded evidence/edit
  interactions in a real browser.
- The RAG index is lexical-only and has no measured retrieval-quality baseline.
- Original Sol assessment design remains experimental planning, appropriately
  not represented as validated work.

## Revised Delivery Assessment

### What the repository can honestly claim today

> Sol has a local, research-first OCEAN assessment MVP that produces
> user-correctable, provenance-bearing profile candidates and can export a
> safety-scoped context packet for model-free generation experiments.

### What it should not yet claim

- a complete Personal Creative Style Kit
- validated personality inference
- complete assessment-version provenance
- production-ready consent or deletion controls
- a closed generation feedback loop
- model-backed personalized artifact generation
- multimodal personalization

## Recommended Remediation Sequence

### Stage 0: Repair correctness and data-control defects

1. Fix confidence fallback and add boundary tests.
2. Validate response IDs and response-scale values.
3. Prevent reviewed atoms from being silently overwritten by rescoring.
4. Add serialized, atomic JSONDB mutation behavior.
5. Persist consent and immutable assessment/scoring provenance.
6. Implement selective deletion semantics and feedback-reference cleanup.
7. Add lifecycle invariant validation.
8. Refresh counts and handoff documentation.

Exit criterion: all defects have focused tests, the full QA suite passes, and
tracked session data remains unchanged.

Status: achieved for the listed Stage 0 defects on 2026-07-12. Automated QA
passes 20 tests, rendered desktop/mobile QA passes, and tracked assessment
storage remains unchanged.

### Stage 1: Complete the safe generation contract

1. Add contextual generation-guidance authoring and review.
2. Persist pilot-run records and bind feedback to exact run atoms.
3. Add evaluation events and a generic baseline comparison.
4. Add output contract validation.
5. Re-run the model-backed gate review.

Exit criterion: a confirmed packet produces an inspectable local artifact, and
feedback is provably attached to the exact run and context that produced it.

### Stage 2: Return to the original wedge

1. Ingest user-provided writing samples with explicit source consent.
2. Extract localized style observations, not broad identity claims.
3. Add liked/disliked examples and direct style calibration.
4. Produce a writing voice guide and one short text artifact.
5. Compare personalized versus generic output using “feels like me” and
   usefulness ratings.
6. Add visual references only after the text loop works.

Exit criterion: one creator/professional can provide authorized examples,
correct the derived style profile, receive a generated artifact, and measure
whether it is more aligned than a generic baseline.

### Stage 3: Platform extraction

Only after the wedge works should the repo extract durable consent, ingestion,
profile, generation, feedback, and deletion services or replace JSONDB with a
multi-user datastore.

## Audit Conclusion

The project is not off course; it chose a narrower assessment-first route and
executed that route substantially. The danger now is mistaking the completeness
of that vertical slice for completion of the original product thesis.

The best next move is not more research ingestion or an external model call.
It is a focused correctness/privacy hardening pass, followed by generation
guidance and persisted pilot provenance, and then a deliberate return to the
original writing-sample-based Creative Style Kit wedge.
