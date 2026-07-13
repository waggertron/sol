# 2026-07-13: Participant Link Validation MVP

## Problem Statement

The existing Creative Style Kit plan is safe but too sequential for fast real
user validation. It waits for full guidance, source intake, observation,
calibration, run-history, and reporting surfaces before testing the core product
question:

> Can the system generate a response that a user says sounds like them?

The next MVP needs a shareable, no-auth participant flow that collects an
organic writing response, assessment evidence, an assessment-informed predicted
response to the same scenario, answer-quality rankings, and user alignment
feedback. It must remain non-diagnostic and must not treat assessment results as
identity facts.

## Options Evaluated

### Option A: Continue The Full Style Kit Sequence

Build the complete guidance workbench, writing-source intake, deterministic
observations, direct calibration, and local product loop before user testing.

| Pros | Cons |
|------|------|
| Preserves the cleanest architecture path | Delays real-user evidence |
| Builds durable product surfaces | Tests many assumptions at once |
| Keeps external provider work deferred | Mock output cannot validate user-perceived voice alignment |

### Option B: Participant-Link Scenario Validation Slice

Create a narrow pilot flow: shareable link, opaque participant ID, fictional
scenario prompt, organic response, assessment, assessment-informed predicted
response, answer-quality ranking, and alignment feedback.

| Pros | Cons |
|------|------|
| Fastest path to real user validation | Adds a pilot-specific flow |
| Separates prompt-answering quality from voice alignment | Requires careful provider/data disclosure |
| Uses existing assessment and run/evaluation foundations | Assessment-only personalization may be weak |

### Option C: Assessment-Only Profile Review Study

Ask users to complete an assessment and rate whether derived atoms feel accurate,
without generating a scenario response.

| Pros | Cons |
|------|------|
| Very fast to run with current app | Does not validate personalized generation |
| Avoids model-provider complexity | Risks optimizing profile copy instead of product value |

## Decision

Choose Option B.

The participant-link MVP becomes the fastest validation path. The broader
Creative Style Kit remains the long-term product direction, but this slice tests
the critical user-perceived outcome sooner.

The predicted response may use assessment outcomes only as a bounded
pilot-context hypothesis for one scenario. It must not use the participant's
organic response as generation input. The UI must frame the predicted response
as a testable attempt, not proof of personality, and all feedback must be stored
as evaluation evidence rather than silently changing assessment claims or atom
confidence.

## Implementation Details

- Add the execution plan in
  `plans/16-participant-link-validation-mvp.md`.
- Use the hosting plan in `plans/17-validation-mvp-hosting.md` and the hosting
  ADR `docs/adr/2026-07-13-vercel-validation-mvp-hosting.md` before sharing the
  MVP with real participants.
- Keep no-auth sharing pilot-only: use an unguessable link plus an opaque
  participant ID that the user is told to write down for resume/export/delete.
- Store a modular scenario record with bounded description length, fictional
  role, recipient, context, and response request.
- Store the organic response before assessment so the assessment does not prime
  the initial writing response.
- Run an existing administrable assessment, preferably Mini-IPIP for the first
  real pilot and TIPI only for a shorter smoke path.
- Generate a predicted response from the same scenario plus assessment-derived
  candidate context, explicitly excluding the organic response.
- Rank the organic and predicted responses against the scenario using a
  prompt-answering rubric separate from voice alignment.
- Ask the participant whether the predicted response sounds like them, with
  structured reasons for alignment or misalignment and optional correction text.
- Persist feedback as run-bound evaluation evidence and mapping-review input.
  Do not automatically mutate raw assessment responses, claims, confidence, or
  model weights.
- External model use requires explicit pilot opt-in and provider disclosure.
  Mock and dry-run modes remain the default for automated tests.
