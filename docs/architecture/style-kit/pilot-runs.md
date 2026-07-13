# Creative Style Kit Pilot Runs

## Scope

`tools/style_kit_pilot.py` creates persisted generic/personalized run pairs from
explicitly selected, eligible guidance. Increment 3 supports only local
`dry-run://style-kit-v1` and deterministic `mock://style-kit-v1` providers.

There is no external provider, credential, network call, route, or UI in this
increment.

The participant-link validation MVP in
`plans/16-participant-link-validation-mvp.md` adds a planned pilot-specific run
shape: one predicted response to a stored fictional scenario, influenced by
assessment-derived candidate context and explicitly excluding the participant's
prior organic response. That predicted-response path must keep the same
provenance discipline: scenario version, assessment/session fingerprint,
context hash, provider version, output validation, and request inspection. It
does not by itself approve a general external provider mode.

## Provider Contract

A provider exposes:

- URI;
- mode;
- provider version;
- optional model identifier;
- `generate(request)`.

Approved modes:

| URI | Behavior |
|---|---|
| `dry-run://style-kit-v1` | Persists the exact run/request contract with empty outputs and `not_run` validation |
| `mock://style-kit-v1` | Produces deterministic contract-shaped writing-guide or project-description output |

Unknown providers, URI/mode mismatches, and external modes fail before a run is
written. Unsupported artifact operations fail loudly.

## Exact Run Provenance

Every run stores:

- owner and source consent references;
- normalized UTC creation/completion timestamps;
- artifact type, requested context, and exact task input;
- task SHA-256;
- prompt contract, provider, and application versions;
- generic and personalized variant IDs;
- per-variant request SHA-256;
- guidance IDs plus a versioned prompt-safe guidance snapshot;
- source, observation, and profile-atom references carried by that guidance;
- personalized context SHA-256;
- output SHA-256 and validation result when output passes.

For participant-link predicted-response runs, provenance must additionally
store `organic_response_excluded: true` and enough request-inspection metadata
to prove the organic response text was not included in the generation request.

The personalized context hash covers consent references, requested context,
source references, profile-atom references, and the complete prompt-safe
guidance snapshot. A guidance edit under the same ID therefore changes the
context hash.

The generic request contains no guidance, guidance snapshot, profile-atom
reference, or personalized context hash. Its request hash depends only on the
shared task, requested context, artifact type, prompt contract, and generic
variant kind. This keeps the comparison control independent from
personalization.

## Atomic Guidance Snapshot

The provider can run only after every selected guidance record passes current
owner, context, task, lifecycle, observation, and profile-atom eligibility
checks.

Before persistence, the repository atomically verifies that each guidance
version and prompt-safe snapshot is still current and eligible. If guidance is
edited, disabled, or otherwise invalidated while generation is occurring, the
run is rejected rather than storing stale provenance.

## Deterministic Mock

Mock output is selected deterministically from the request hash. Repeating the
same task, context, guidance snapshot, and prompt version produces the same
request hashes and outputs even when run IDs or timestamps differ.

The mock demonstrates provider and persistence behavior only. It is not
evidence of personalization quality or model readiness.

## Output Validation

The local validator enforces:

- non-empty string output;
- a 5,000-character ceiling;
- a 35-300 word project-description range;
- four required writing-guide sections;
- exclusion of diagnostic, protected-trait, mind-reading, fixed-identity, and
  system-message framing.

Failed provider output is not stored. The run is persisted as `failed` with
validation errors, while output content and output hash remain null.

## Time Contract

Inbound run timestamps accept ISO-8601 strings with `Z` or an explicit offset.
They are normalized through `tools/time_contracts.py` and stored as UTC `Z`
strings because the existing JSON contracts use display/audit timestamps.
Blank, malformed, or timezone-free values fail explicitly.

## Local Artifacts And Cleanup

Automated tests use self-cleaning temporary repositories. Manual runs use the
same ignored default repository documented in `local-repository.md`:

```bash
rm -f tmp/style-kit/style-kit-records.json
```

No process, port, container, cache, or separate output directory is created.

## Validation

```bash
python3 -m unittest tests.test_style_kit_pilot
python3 tools/validate_style_kit_contracts.py
./scripts/run_assessment_web_mvp_qa.sh
```

Tests cover dry-run persistence, deterministic mock read-after-write,
generic-context isolation, writing-guide structure, ineligible-guidance
exclusion before provider calls, external/unsupported rejection, output
redaction, hash tampering, timestamp boundaries, and mid-run guidance changes.
