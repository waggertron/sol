# Creative Style Kit Validated Execution Ledger

## Purpose

Turn `plans/14-personal-creative-style-kit-roadmap.md` into small implementation
increments that can be completed and validated independently.

The rule for this ledger is simple: do not mark an increment complete because
files exist. Mark it complete only when its acceptance behavior is observable,
its targeted tests pass, the full assessment regression suite remains green,
and tracked user data is unchanged.

## Validation Ladder

Every increment uses the cheapest relevant checks first:

1. JSON/schema or Python syntax checks.
2. Focused unit/contract tests for the changed boundary.
3. Focused HTTP/static checks when routes or UI change.
4. Full local regression QA.
5. Rendered desktop/mobile QA only when visible UI changes.

Baseline commands:

```bash
python3 tools/validate_style_kit_contracts.py
python3 -m unittest tests.test_style_kit_contracts
./scripts/run_assessment_web_mvp_qa.sh
```

Tests must use temporary storage. Manual run artifacts must stay under ignored
`tmp/` paths. No increment may require network access or credentials.

## Increment 0: Contract Foundation

Status: complete.

Delivered:

- [x] First audience and artifacts fixed: independent creators and knowledge
  workers calibrating their own professional writing; writing guide plus a
  150-300 word project description.
- [x] ADR selects independent source, observation, guidance, pilot-run, and
  evaluation records.
- [x] Five versioned JSON Schemas and one cross-linked valid bundle.
- [x] Self-authored-only, local-until-deleted, no-external-provider policy.
- [x] Offline schema and cross-record validator.
- [x] Tests for valid shape, ownership, references, guidance eligibility,
  source deletion, and external-provider rejection.
- [x] Development/operator dependency manifest.

Validation gate:

- contract validator reports zero errors;
- five focused tests pass;
- full assessment regression suite passes;
- tracked assessment storage remains unchanged.

## Increment 1: Contract-Backed Local Repository

Goal: persist the new records without adding UI or generation behavior.

Status: complete. Eight focused repository tests and the full 38-test suite
pass; tracked assessment storage is unchanged.

Implementation:

- [x] Add a repository interface for loading, listing, getting, creating, and
  replacing a versioned Style Kit bundle.
- [x] Add a local JSONDB implementation with atomic same-directory replacement
  and in-process mutation serialization.
- [x] Select storage through an environment variable; tests always use a
  temporary path and manual defaults remain under ignored `tmp/` storage.
- [x] Validate the full bundle before every successful write.
- [x] Reject duplicate IDs, owner mismatches, dangling references, invalid
  lifecycle states, and unapproved external runs.
- [x] Return copies so callers cannot mutate persisted state out of band.

Acceptance:

- create/read works for each of the five record types;
- an invalid write leaves the stored bundle byte-for-byte unchanged;
- concurrent in-process mutations do not lose records;
- no test changes tracked JSONDB files.

Validation:

```bash
python3 -m unittest tests.test_style_kit_store
python3 tools/validate_style_kit_contracts.py
./scripts/run_assessment_web_mvp_qa.sh
```

## Increment 2: Guidance Lifecycle

Goal: make concrete contextual guidance a first-class, user-reviewed record.

Status: complete. Seven focused guidance tests and the full 45-test suite pass;
tracked assessment storage is unchanged.

Implementation:

- [x] Add create/review/disable operations for guidance.
- [x] Allow `proposed -> confirmed|edited|disabled` and
  `confirmed|edited -> edited|disabled`; reject invalid transitions.
- [x] Preserve `original_instruction` and append field-level review history.
- [x] Keep prompt-safe text separate from raw source/evidence text.
- [x] Require at least one valid observation or eligible profile-atom reference.
- [x] Do not automatically convert broad OCEAN claims into guidance.

Acceptance:

- only confirmed/edited active guidance is generation-eligible;
- edits preserve original wording and append history;
- rejected/suppressed/review-only/blocked atom evidence cannot activate
  guidance;
- disabling guidance immediately removes it from future run context.

Validation:

```bash
python3 -m unittest tests.test_style_kit_guidance
./scripts/run_assessment_web_mvp_qa.sh
```

## Increment 3: Dry-Run And Deterministic Mock Pilot

Goal: create and read persisted generic/personalized runs without a real model.

Implementation:

- [ ] Define one provider interface used by `dry-run` and `mock://`.
- [ ] Make `mock://` output deterministic from task and context hashes.
- [ ] Create generic and personalized variants from the same task input.
- [ ] Persist exact source, atom, guidance, prompt-contract, and provider
  versions plus content hashes.
- [ ] Add bounded output structure/safety validation.
- [ ] Fail loudly for unsupported provider operations.

Acceptance:

- create then read returns one run with exactly two variants;
- repeated mock inputs produce the same outputs and hashes;
- generic variants contain no personalization references;
- ineligible evidence cannot enter the personalized request;
- external mode remains rejected.

Validation:

```bash
python3 -m unittest tests.test_style_kit_pilot
python3 tools/validate_style_kit_contracts.py
./scripts/run_assessment_web_mvp_qa.sh
```

## Increment 4: Evaluation Binding

Goal: bind feedback to what the user actually saw.

Implementation:

- [ ] Create evaluation events only for known completed runs.
- [ ] Record the blinded choice before revealing variant identity.
- [ ] Validate “feels like me” and usefulness ratings.
- [ ] Restrict affected guidance to guidance used by the personalized variant.
- [ ] Require correction text for wrong/too-strong/too-generic labels.
- [ ] Never mutate assessment responses, claims, or confidence from an event.

Acceptance:

- unknown runs and unused guidance are rejected;
- event creation does not change source, observation, atom, or guidance claims;
- events are exportable and independently deletable.

Validation:

```bash
python3 -m unittest tests.test_style_kit_evaluation
./scripts/run_assessment_web_mvp_qa.sh
```

## Increment 5: Guidance And Run-History Workbench

Goal: expose the completed guidance/run/evaluation contracts in the local UI.

Implementation:

- [ ] Add guidance list/review/disable routes and UI.
- [ ] Add run create/list/show/export/delete routes and UI.
- [ ] Add blinded generic/personalized comparison and evaluation form.
- [ ] Show evidence, context, uncertainty, contraindications, and exact run
  provenance without presenting style as identity.
- [ ] Preserve usable mobile navigation and focus/error behavior.

Acceptance:

- one user can review guidance, create a mock run, compare variants, and save
  feedback through the browser;
- HTTP failures are visible and do not silently change UI state;
- desktop/mobile rendered QA shows no clipping or unreachable controls.

Validation:

```bash
./scripts/run_assessment_web_mvp_qa.sh
./scripts/run_assessment_web_mvp_visual_qa.sh
```

## Increment 6: Pasted Writing Source And Cascading Deletion

Goal: add the first authorized non-assessment input.

Implementation:

- [ ] Add pasted-text intake only; file upload remains deferred.
- [ ] Require self-authorship, consent version, allowed uses, context, and a
  no-third-party-content/redacted declaration.
- [ ] Persist checksum and source provenance locally.
- [ ] Add source list/show/export/delete routes and UI.
- [ ] Implement and test deletion cascade: redact source content, invalidate
  observations, disable unsupported guidance, and redact requested run content.

Acceptance:

- a user can inspect and export everything derived from one source;
- deletion removes raw source content and leaves no copied excerpt in dependent
  active records;
- the invalidation cascade is atomic;
- no source is transmitted externally.

Validation:

```bash
python3 -m unittest tests.test_style_kit_sources
./scripts/run_assessment_web_mvp_qa.sh
./scripts/run_assessment_web_mvp_visual_qa.sh
```

## Increment 7: Deterministic Writing Observations

Goal: derive reproducible, localized style evidence without trait inference.

Implementation:

- [ ] Add sentence/paragraph length, punctuation/list, heading/structure,
  pronoun, contraction/hedging, and lexical repetition/density extractors.
- [ ] Version every extractor and bind evidence to exact source locations.
- [ ] Present values and limitations as observations, not identity claims.
- [ ] Add confirm/reject/context/counterexample controls.

Acceptance:

- the same source and extractor versions produce byte-identical observations;
- every observation traces to a source and method;
- protected, clinical, competence, and morality inference terms are absent;
- deletion invalidates all derived observations.

Validation:

```bash
python3 -m unittest tests.test_style_observations
./scripts/run_assessment_web_mvp_qa.sh
```

## Increment 8: Direct Style Calibration

Goal: capture explicit contextual preferences without requiring assessment.

Implementation:

- [ ] Add 8-12 controls across directness, brevity, structure, warmth,
  abstraction, metaphor, energy, and exploratory framing.
- [ ] Include professional, public, reflective, and creative contexts.
- [ ] Support forced choice, neither, and context-dependent answers.
- [ ] Produce proposed guidance that requires confirmation/editing.

Acceptance:

- calibration completes without OCEAN;
- no calibration answer is mapped back into a broad personality claim;
- every activated guidance item is user-confirmed or edited.

Validation:

```bash
python3 -m unittest tests.test_style_calibration
./scripts/run_assessment_web_mvp_qa.sh
./scripts/run_assessment_web_mvp_visual_qa.sh
```

## Increment 9: Complete Local Product Loop

Goal: prove the v1 journey locally before any external provider.

Scenario:

```text
consent -> source -> observations -> guidance -> mock A/B run
        -> blinded choice -> correction -> rerun -> export/delete
```

Acceptance:

- the scenario completes without assessment, credentials, or network;
- every output is reproducible from a persisted run;
- correction affects the next run only through reviewed guidance;
- export and cascading deletion cover the complete graph;
- an end-to-end exclusion test proves ineligible atoms never enter a request.

Validation:

```bash
python3 -m unittest tests.test_style_kit_end_to_end
./scripts/run_assessment_web_mvp_qa.sh
./scripts/run_assessment_web_mvp_visual_qa.sh
```

## Increment 10: Product Evaluation Gate

Goal: decide whether real-model work is justified.

Implementation:

- [ ] Approve a consenting-participant protocol and deletion procedure.
- [ ] Run blinded generic-versus-personalized comparisons.
- [ ] Report preference, feels-like-me, usefulness, correction, completion,
  comprehension, and deletion outcomes.
- [ ] Record a proceed/revise/narrow/stop decision.

Gate:

No external model, visual generation, or platform extraction begins merely
because the local implementation is complete. A separate ADR must approve one
provider/model/task combination after the local product and safety evidence is
reviewed.

## Current Next Step

Implement Increment 3 only: persisted dry-run and deterministic `mock://` pilot
runs with output validation. Do not add routes or UI in that change.
