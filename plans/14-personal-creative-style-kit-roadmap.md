# Personal Creative Style Kit Product Roadmap

## Purpose

Turn the current assessment/profile foundation into the first product wedge that
demonstrates useful, consented, user-correctable personalization.

This plan is grounded in:

- `docs/inventory/2026-07-12-capability-inventory.md`
- `docs/audits/2026-07-12-initial-plan-progress-audit.md`
- `plans/01-product-vision.md`
- `plans/02-first-wedge.md`
- `plans/12-post-audit-roadmap.md`

## Product Goal v1

A user can provide authorized writing examples and direct style preferences,
inspect and correct the resulting style profile, generate one writing guide and
one short text artifact, compare personalized and generic results, and delete or
export every source, profile, run, and feedback record.

The product must preserve provenance, uncertainty, context, and user control.
It must not present personality assessment results as identity facts or use
broad traits as direct global writing controls.

## Recommended Product Strategy

### Primary wedge

Start with creators and professionals who want generated writing to feel more
like their preferred voice.

This is a working assumption, not validated positioning. The initial pilot
should test whether this audience and problem are real before platform
extraction or multimodal expansion.

### Input priority

1. direct style choices and corrections;
2. user-provided writing samples;
3. liked/disliked writing examples;
4. optional assessment context;
5. visual references only after the text loop demonstrates value.

### Why this order

Writing behavior and explicit preferences are closer to the generated artifact
than broad OCEAN traits. They provide more auditable, task-relevant evidence and
reduce pressure to translate trait labels into speculative style rules.

## Brainstormed Strategy Options

| Option | Strength | Risk | Decision |
|---|---|---|---|
| Continue assessment-first | Reuses the strongest current implementation | Broad traits are weak direct generation controls; may feel like a personality quiz rather than a creative tool | Keep assessment optional, not the main wedge |
| Writing-sample-first | Directly observes voice/style signals relevant to text | Extraction can overclaim authorship or stable identity; uploaded text may contain third-party data | Recommended primary evidence with explicit consent and localized observations |
| Preference-pair-first | Very explicit user agency; easy to correct | Can be tedious and may measure only presented options | Recommended companion input and onboarding shortcut |
| Prompt/preset-only | Fastest visible product | Provides little durable evidence model and weakens the project thesis | Use only as a generic baseline/control |
| Moodboard/visual-first | Attractive demo and future multimodal alignment | Higher model/provider complexity and harder evaluation | Defer until text loop works |
| Platform/API-first | Reusable architecture | Premature abstraction before product value | Defer until the wedge demonstrates repeated value |

## North-Star Outcome

> A user prefers the personalized artifact over a generic baseline and can
> explain, inspect, and correct the profile evidence that caused the difference.

Supporting outcomes:

- users understand that profile claims are tentative and scoped;
- profile corrections persist and affect later runs;
- deletion/export behavior is trustworthy;
- blocked or review-only atoms never reach generation;
- the system learns style guidance from direct feedback without silently
  converting it into personality certainty.

## v1 Scope

### Inputs

- 3-5 user-authored writing samples or excerpts;
- a short direct style calibration;
- 5-10 liked/disliked or forced-choice writing comparisons;
- optional existing OCEAN assessment session;
- direct edits and notes.

### Profile outputs

- communication/style observations tied to source excerpts or deterministic
  features;
- explicit style preferences;
- contextual generation guidance;
- confidence and uncertainty;
- counterexamples and user corrections;
- source and consent provenance.

### Generated outputs

- writing/communication style guide;
- one short artifact, recommended first: a 150-300 word professional bio,
  introduction, or project description;
- generic control artifact using the same task without profile context.

### Feedback

- personalized vs generic preference;
- “feels like me” rating;
- usefulness rating;
- too strong / too generic / wrong;
- direct correction;
- per-guidance enable/disable or edit.

### Explicitly out of scope for v1

- clinical or diagnostic interpretation;
- passive surveillance or hidden data collection;
- protected-trait inference;
- eligibility use;
- multi-user production deployment;
- automated social-account ingestion;
- image, audio, avatar, video, or agent-persona generation;
- validated claims for the experimental Sol OCEAN candidate.

## User Journey

1. User chooses the writing-style kit and sees the data/consent explanation.
2. User adds writing samples, marks authorship/permission, and chooses allowed
   uses and retention.
3. User completes direct style calibration and optional preference pairs.
4. System creates source-bound observations, not personality labels.
5. User confirms, edits, rejects, or scopes proposed style atoms.
6. User writes/edits concrete generation guidance.
7. System creates a persisted pilot run using a local/mock provider by default.
8. User compares personalized and generic artifacts without knowing which is
   which until after choosing.
9. User rates, corrects, exports, or deletes the profile/run/source data.
10. Later runs use only eligible guidance and preserve prior feedback provenance.

## UI Evolution

```text
  CURRENT ASSESSMENT MVP                 TARGET STYLE KIT v1
  ┌────────────┬──────────────┐          ┌────────────┬──────────────────────┐
  │ Instruments│ Administer   │          │ Sources    │ Add writing samples  │
  │ Resume     │ Scores       │          │ Calibrate  │ Compare preferences  │
  │ Sessions   │ Profile atoms│          │ Profile    │ Review style atoms   │
  │            │ Evidence     │          │ Guidance   │ Edit scoped guidance │
  │            │              │          │ Generate   │ Compare A/B artifacts│
  │            │              │          │ History    │ Runs and feedback    │
  └────────────┴──────────────┘          └────────────┴──────────────────────┘
  Assessment proves profile lifecycle.   Direct style evidence closes the loop.
```

Mobile target:

```text
┌──────────────────────────────┐
│ Style Kit                    │
├──────────────────────────────┤
│ Sources  Calibrate  Profile  │
├──────────────────────────────┤
│ Current step                 │
│ ┌──────────────────────────┐ │
│ │ source / atom / artifact │ │
│ │ evidence and controls    │ │
│ └──────────────────────────┘ │
├──────────────────────────────┤
│ [Back]            [Continue] │
└──────────────────────────────┘
```

## Target Local Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│ Browser UI                                                       │
├──────────────┬───────────────┬──────────────┬─────────────────────┤
│ Source intake│ Profile review│ Guidance     │ Generate/evaluate   │
└──────┬───────┴───────┬───────┴──────┬───────┴──────────┬──────────┘
       │               │              │                  │
┌──────┴───────────────┴──────────────┴──────────────────┴──────────┐
│ Shared application contracts                                    │
├──────────────┬───────────────┬──────────────┬─────────────────────┤
│ Consent/source│ Observations  │ Profile atoms│ Pilot/evaluation    │
└──────┬────────┴───────┬───────┴──────┬───────┴──────────┬──────────┘
       │                │              │                  │
┌──────┴──────┐ ┌───────┴──────┐ ┌─────┴────────┐ ┌───────┴─────────┐
│ Local JSONDB│ │ Deterministic│ │ Context      │ │ mock:// provider│
│ providers   │ │ extractors   │ │ packet       │ │ real provider   │
│             │ │ first        │ │ builder      │ │ opt-in later    │
└─────────────┘ └──────────────┘ └──────────────┘ └─────────────────┘
```

Production services are not required for the first closed local loop. Provider
interfaces and persisted schemas should be designed so the local/mock path uses
the same contracts as a future external model.

## Core Data Contracts To Add

### Source record

- source id and owner/user id;
- source type (`writing_sample`, `liked_example`, `direct_preference`);
- consent version/time/scope;
- authorship/permission declaration;
- original content or explicit ephemeral-processing marker;
- checksum, created time, retention/deletion state;
- contexts and allowed downstream uses.

### Observation

- observation id;
- source id and evidence location/excerpt;
- observation type (`sentence_length_pattern`, `directness_preference`, etc.);
- extraction method/version;
- context, confidence, counterevidence;
- sensitivity and permitted inference level;
- user visibility.

### Style atom

Reuse the current profile atom lifecycle, adding source types and style domains
without weakening assessment boundaries.

### Generation guidance

- guidance id and atom references;
- concrete instruction;
- context/task scope;
- user state (`proposed`, `confirmed`, `edited`, `disabled`);
- source and review history;
- contraindications;
- prompt-safe representation.

### Pilot run

- run id, mode, provider, model/provider version;
- prompt-contract version;
- task input and generic/personalized variant identifiers;
- exact guidance/atom references and context hash;
- timestamps, output metadata, validation result;
- deletion/export state.

### Evaluation event

- run/variant id;
- blinded preference choice;
- “feels like me” and usefulness values;
- categorical and free-text correction;
- affected guidance references;
- recorded time and provenance.

## Provider Strategy

Every generation surface must support:

- `dry-run`: serialize prompt, context, and validation without output;
- `mock://`: deterministic contract-shaped output for local UI/API integration;
- external provider: disabled by default and added only after gate review.

The mock must support create/read of a run and both personalized/generic
variants. Automated tests must never require credentials or network access.

## Phased Execution Plan

### Phase 0: Plan And Contract Foundation

Goal: remove ambiguity before adding user data or generation.

Status: complete. Contract validation and the current full 54-test regression
suite pass.

Tasks:

- [x] Confirm the first audience and artifact: independent creators and
  knowledge workers, style guide plus a 150-300 word project description.
- [x] Write an ADR for source/observation/guidance/pilot/evaluation ownership.
- [x] Define machine-readable schemas and versioning for new records.
- [x] Add a declared development dependency path for `beautifulsoup4` or isolate
  the acquisition helper more explicitly.
- [x] Refresh tracked sample sessions/artifacts to current schema or label them
  permanently historical; the inventory labels them historical examples.
- [x] Define retention defaults and third-party-content handling.

Acceptance:

- every new record has owner, provenance, timestamps, consent, version, export,
  and deletion semantics;
- no external credentials are required;
- the current assessment flow remains green.

### Phase 1: Generation Guidance And Persisted Pilot Runs

Goal: complete the existing generation contract before introducing writing
uploads.

Tasks:

- [ ] Add user-editable contextual generation guidance to profile atoms.
- [x] Enforce guidance lifecycle and prompt-safe representation.
- [x] Persist pilot runs with exact atom/guidance references and context hash.
- [ ] Require feedback to target a known run and used guidance.
- [x] Add output schema/safety validator.
- [x] Add `dry-run` and deterministic `mock://` providers behind one interface.
- [ ] Add workbench Guidance and Run History surfaces.

Acceptance:

- a confirmed guidance set creates persisted generic and personalized mock runs;
- feedback cannot reference unknown/unused guidance;
- suppressed/rejected/review-only/blocked atoms cannot enter either request;
- runs, outputs, and feedback can be exported and deleted.

### Phase 2: Writing Source Intake

Goal: add the first non-assessment evidence source safely.

Tasks:

- [ ] Add source-level consent with allowed uses and retention.
- [ ] Support pasted text first; file upload comes after the contract works.
- [ ] Require authorship/permission declaration and warn about third-party data.
- [ ] Store source checksum and versioned provenance.
- [ ] Add source list, inspect, export, and delete controls.
- [ ] Add deterministic observations first:
  - sentence/paragraph length distributions;
  - punctuation and list usage;
  - heading/structure patterns;
  - first/second-person usage;
  - contraction and hedging indicators;
  - lexical repetition/density indicators.
- [ ] Present observations as localized evidence, not trait inference.
- [ ] Add counterexample/context controls.

Acceptance:

- user can trace every observation to a source and method version;
- deletion removes or invalidates dependent observations/atoms/runs;
- deterministic extraction is reproducible and contract-tested;
- no protected or clinical inference is emitted.

### Phase 3: Direct Style Calibration

Goal: obtain explicit generation-relevant preferences rather than inferring
them from broad traits.

Tasks:

- [ ] Define 8-12 contextual controls, such as directness, brevity, structure,
  warmth, abstraction, metaphor, energy, and exploratory/conventional framing.
- [ ] Distinguish task contexts: professional, public, reflective, creative.
- [ ] Add forced-choice examples and “neither/context-dependent” responses.
- [ ] Turn direct choices into provisional style atoms and proposed guidance.
- [ ] Let users edit wording and scope before activation.
- [ ] Avoid mapping choices back into broad personality claims.

Acceptance:

- every active guidance item is directly confirmed/edited by the user;
- users can express context dependence and counterpreferences;
- calibration can complete without taking an OCEAN assessment.

### Phase 4: Style Profile And Local Artifact Loop

Goal: produce the first complete local Creative Style Kit experience using
`mock://` and dry-run behavior.

Tasks:

- [ ] Merge writing observations, direct preferences, and optional assessment
  context without collapsing their evidence types.
- [ ] Add a style-profile summary organized by communication guidance, context,
  evidence, uncertainty, and contraindications.
- [ ] Produce a deterministic/mock writing guide.
- [ ] Produce personalized and generic mock artifacts for the same task.
- [ ] Add blinded A/B reveal and correction UI.
- [ ] Persist runs and evaluation events.

Acceptance:

- one user can complete source → profile → guidance → run → comparison →
  correction → rerun locally;
- every output is reproducible from its run record;
- no output requires an external model.

### Phase 5: Evaluation Pilot

Goal: test whether the wedge is useful before adding a real provider.

Tasks:

- [ ] Write a small consenting-participant protocol and data-deletion process.
- [ ] Define primary endpoint: blinded personalized-vs-generic preference.
- [ ] Define secondary endpoints: “feels like me,” usefulness, correction rate,
  completion, trust/comprehension, and deletion success.
- [ ] Add aggregate local reporting with no diagnostic interpretation.
- [ ] Conduct qualitative review of wrong/too-strong/too-generic outputs.
- [ ] Decide whether to revise, narrow, proceed, or stop.

Initial decision hypotheses—not scientific claims:

- personalized selected over generic in at least 60% of comparisons;
- median “feels like me” and usefulness at least 4/5;
- 100% blocked-atom exclusion and requested deletion success;
- users can correctly explain that profile claims are editable evidence, not
  identity facts.

Sample size and statistical interpretation require a separate justified pilot
protocol; these values are product decision targets only.

### Phase 6: External Model Gate

Goal: decide whether model-backed generation is justified and safe.

Required before approval:

- [ ] Phase 1 provenance/output gates pass.
- [ ] Local closed-loop evaluation works.
- [ ] Provider abstraction and mock integration tests are green.
- [ ] Explicit user opt-in and data-sent-to-provider copy exist.
- [ ] Output validator and incident/disable path exist.
- [ ] Cost, retention, provider logging, and deletion behavior are documented.
- [ ] A new ADR approves one provider/model/task combination.

If approved:

- enable only one low-risk writing task;
- retain dry-run and mock as defaults for development/tests;
- compare provider output against the same generic baseline;
- do not use the experimental Sol OCEAN candidate.

### Phase 7: Visual Style Expansion

Goal: extend a validated text loop into visual direction.

Tasks:

- [ ] Add consented image/moodboard source contract.
- [ ] Begin with explicit ratings/tags and user-authored descriptions.
- [ ] Add visual-direction profile atoms and guidance separately from traits.
- [ ] Produce image-prompt direction before direct image generation.
- [ ] Define visual comparison/evaluation and provider gate.

Do not begin until the text wedge demonstrates value and source consent/deletion
works across non-assessment data.

### Phase 8: Platform Extraction

Goal: extract reusable services only after repeated wedge evidence.

Potential work:

- transactional multi-user datastore and migrations;
- authentication/authorization and tenant isolation;
- consent/source/profile/generation services;
- provider operations, observability, rate/cost controls;
- API/SDK boundary;
- deployment and security review.

This is not on the current critical path.

## Cross-Cutting Workstreams

### Safety and consent

- source-level permission and retention;
- third-party-content handling;
- sensitive/blocked inference gates;
- provenance and user-visible explanations;
- export and cascading deletion tests.

### Evaluation

- generic controls;
- blinded comparisons;
- direct corrections;
- comprehension/trust checks;
- no validity claims from satisfaction alone.

### Research

- retrieve and promote sources only when they answer a current product/metric
  question;
- prioritize explainable personalization, writing-style measurement, preference
  elicitation, and consent UX;
- keep experimental assessment validation as a parallel, non-critical track.

### Quality

- contract tests at every boundary;
- isolated temporary storage for tests;
- rendered UI QA and accessibility checks;
- current-schema fixtures;
- no network or credentials in the default suite.

## Dependency And Gate Map

| Capability | Depends on | Blocks |
|---|---|---|
| Guidance authoring | current atom lifecycle | meaningful generation |
| Pilot-run persistence | guidance schema + context packet | trustworthy feedback/model gate |
| Writing intake | source consent/deletion contract | direct style evidence |
| Direct calibration | style domain/guidance schema | active task controls |
| Mock artifact loop | provider interface + pilot runs | end-to-end UX/evaluation |
| Evaluation | generic baseline + run records | real-provider decision |
| External model | all generation/evaluation safety gates | real artifact pilot |
| Visual expansion | validated text loop + image consent | multimodal wedge |
| Platform extraction | demonstrated wedge/repeated operations | production/API path |

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| Personality quiz overshadows creative value | Make assessment optional; lead with writing/preferences |
| Style observations become identity claims | Keep source-local wording, context, uncertainty, correction |
| Uploaded text includes third-party/private content | Permission declaration, warnings, source scopes, deletion |
| User wants imitation of another living person | Constrain v1 to user's own authorized style evidence and explicit preferences |
| Guidance becomes prompt injection | Structured fields, system/data separation, validation, bounded text |
| Feedback silently changes psychological claims | Update guidance notes, not assessment confidence/claim automatically |
| Mock success does not translate to model quality | Use mock for contracts only; require blinded real-output pilot later |
| Evaluation satisfaction is mistaken for construct validity | Separate product usefulness from psychometric validation |
| Premature platform rebuild | Keep local contracts/providers until wedge evidence exists |
| Research ingestion becomes the product | Tie new research work to explicit roadmap decisions |

## Product Decisions To Make

### Decided for the first local slice

- audience: independent creators and knowledge workers;
- first short artifact: a 150-300 word project description;
- companion artifact: a writing/communication style guide;
- source retention: local until explicit deletion;
- source permission: self-authored writing only in v1.

### Decide before Phase 1 completion

- style guidance granularity and supported contexts beyond the initial
  professional/project-description path.

### Decide at the Phase 5 gate

- whether measured user value justifies a real model provider;
- whether the product should remain creator-focused or become a reusable profile
  layer;
- whether OCEAN adds useful optional context or unnecessary onboarding burden;
- whether visual direction is the next modality.

## Immediate Execution Backlog

Recommended next implementation sequence:

1. Bind evaluation events to exact completed runs and used guidance.
2. Build Guidance, Run History, and blinded comparison UI.
3. Add pasted writing-source consent/storage/cascading deletion.
4. Add deterministic writing observations.
5. Add direct style calibration.
6. Close the local mock artifact/evaluation loop.
7. Run the product-value gate before any real model or visual work.

The acceptance behavior and validation command for each increment live in
`plans/15-style-kit-validated-execution.md`.

## Definition Of Done For Product Goal v1

- [ ] User completes the flow without an OCEAN assessment.
- [ ] At least one authorized writing source and one direct preference contribute
  to the profile.
- [ ] Every observation/atom/guidance item is inspectable and correctable.
- [ ] Personalized and generic variants share the same task and are compared
  blind.
- [ ] Run records reproduce exact context and prompt versions.
- [ ] Feedback is bound to the exact run and guidance used.
- [ ] Export and cascading deletion cover sources, profile, runs, and feedback.
- [ ] Safety tests prove ineligible atoms cannot reach generation.
- [ ] Product pilot meets or deliberately revises the decision targets.
- [ ] No claim exceeds the evidence or presents assessment results as identity.

## Roadmap Maintenance

- Update this ledger when a phase passes its acceptance gate.
- Record architecture decisions in `docs/adr/`.
- Keep `docs/current-state.md`, `docs/project-memory.md`, and the README aligned
  with completed—not merely planned—capabilities.
- Add new research to product behavior only through reviewed promotion.
- Keep experimental-assessment work in `plans/13` and off the product critical
  path until external review/validation evidence exists.
- Execute implementation through the small validation gates in `plans/15`.
