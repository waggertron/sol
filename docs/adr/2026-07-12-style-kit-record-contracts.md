# 2026-07-12: Creative Style Kit Record Contracts

## Problem Statement

The assessment MVP stores assessment sessions, scores, profile atoms, and
feedback in one local JSONDB boundary. The Creative Style Kit adds five new
record types with different ownership and lifecycle needs:

- user-provided sources;
- source-local observations;
- user-reviewed generation guidance;
- persisted generic/personalized pilot runs;
- blinded evaluation events.

Embedding these records directly into assessment sessions would make assessment
optional in the UI but mandatory in storage. Moving immediately to production
services would add authentication, deployment, and database work before the
product wedge has demonstrated value.

The first implementation must remain local, credential-free, source-traceable,
exportable, and deletable. It must also preserve the existing distinction
between self-report assessment evidence and direct style evidence.

## Options Evaluated

### Option A: Extend Assessment Sessions With Style Kit Fields

Store sources, observations, guidance, runs, and evaluations as nested fields
inside the current assessment-session records.

| Pros | Cons |
|------|------|
| Reuses one JSON file and current APIs | Makes assessment sessions the owner of unrelated writing evidence |
| Few new persistence primitives | Complicates source deletion and cross-session profile use |
| Fast initial implementation | Prevents an assessment-optional product path |

### Option B: Versioned Independent Records Behind A Shared Local Boundary

Define five independent record contracts joined by stable identifiers. Persist
them through a dedicated local repository boundary, initially backed by an
isolated JSONDB file. Keep generation providers separate from storage and make
`dry-run` and `mock://` the only approved modes.

| Pros | Cons |
|------|------|
| Assessment remains optional evidence | Adds schemas and cross-record validation |
| Clear ownership, export, and cascading deletion | Local JSONDB is still single-process |
| Same contracts can support later transactional storage | Requires a repository boundary before UI work |
| Supports offline mock generation and deterministic tests | More initial contract work |

### Option C: Build Production Services And A Transactional Database Now

Create separate source, profile, generation, and evaluation services with
authentication and a production database.

| Pros | Cons |
|------|------|
| Strong multi-user and transaction foundation | Premature before product value is demonstrated |
| Natural service ownership | Adds deployment, auth, migration, and operational scope |
| Easier future scaling | Slows the first local closed-loop evaluation |

## Decision

Choose Option B.

The five records are independent, versioned documents with explicit `owner_id`,
provenance, consent reference, timestamps, export state, and deletion state.
References between records are identifiers, not nested mutable copies. The
assessment session/profile-atom store remains unchanged and may be referenced
as optional evidence.

For the first local product slice:

- the supported audience is an independent creator or knowledge worker
  calibrating their own professional writing voice;
- the first generated artifacts are a writing guide and a 150-300 word project
  description;
- writing sources must be self-authored; third-party or uncertain authorship is
  rejected rather than inferred around;
- the retention default is local storage until explicit deletion, with the
  source content and its consent receipt visible to the user;
- no source content is sent to an external provider;
- `dry-run` and deterministic `mock://` generation use the same pilot-run
  contract; external providers remain disabled;
- direct preferences and writing observations remain separate from OCEAN
  self-report evidence and do not become personality facts.

2026-07-13 update: `docs/adr/2026-07-13-participant-link-validation-mvp.md`
defines a separate validation shortcut. That MVP may request a narrow
pilot-provider gate for one predicted scenario response after explicit provider
disclosure and request-inspection tests. This does not approve a general
external-provider mode for the Creative Style Kit contracts.

Local-until-deleted is chosen over an undocumented ephemeral mode because the
first wedge requires inspectable evidence, reproducible extraction, correction,
export, and cascading deletion. A future derived-only mode needs its own threat,
reproducibility, and invalidation review before it is offered.

## Implementation Details

### Contract locations

- Store JSON Schemas below `schemas/style_kit/v1/`.
- Use explicit schema identifiers such as `sol.style-kit.source.v1`.
- Keep valid cross-linked examples below `schemas/style_kit/v1/examples/`.
- Validate both JSON Schema shape and cross-record references with
  `tools/validate_style_kit_contracts.py`.

### Ownership and references

- `source` owns the raw authorized text and consent receipt.
- `observation` references one source and records the extraction method,
  localized evidence, uncertainty, and permitted inference level.
- `generation_guidance` references observations, profile atoms, and sources;
  only confirmed or user-edited guidance may enter a personalized run.
- `pilot_run` records both generic and personalized variants, exact guidance
  and atom references, context hash, provider mode, output metadata, and
  validation state.
- `evaluation_event` references one persisted run and records a blinded choice,
  ratings, and optional corrections without rewriting evidence.

### Deletion behavior

- Deleting a source removes its raw content and marks dependent observations
  invalidated.
- Guidance with no remaining valid evidence becomes disabled.
- Existing runs retain only the minimum auditable metadata permitted by the
  user's deletion request; raw task/output content is removed when the run is
  deleted.
- Evaluation events are independently exportable and deletable and must never
  keep deleted source text by copy.
- The first persistence implementation must test the complete cascade before
  source intake is exposed in the UI.

### Local/mock boundary

- The first persistence provider will be an isolated local JSONDB repository.
- The generation provider interface must support `dry-run` and `mock://` before
  any external implementation.
- `mock://` must support create/read of both run variants and deterministic
  output suitable for local integration tests.
- Automated tests use temporary storage and require no credentials or network.
- Manual artifacts remain under ignored `tmp/` paths.

### Dependencies

Runtime assessment and RAG paths remain Python-standard-library based. Optional
operator and contract-validation dependencies are declared in
`requirements-dev.txt`, including `beautifulsoup4` and `jsonschema`. This makes
the existing HTML acquisition helper and the new schema validator reproducible
without turning either dependency into a production runtime requirement.

### Follow-up increments

1. Implement and test the five schemas and valid example bundle.
2. Add a dedicated repository interface and isolated JSONDB implementation.
3. Implement generation-guidance lifecycle and persisted run creation.
4. Add deterministic `mock://` generation and output validation.
5. Prove export and cascading deletion before source-intake UI work.
