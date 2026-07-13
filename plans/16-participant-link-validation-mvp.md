# Participant Link Voice Validation MVP

## Purpose

Validate the core product claim as quickly as possible:

> A participant reads a fictional scenario, writes their own response, completes
> an assessment, then judges whether an assessment-informed predicted response
> sounds like them.

This MVP measures perceived voice alignment and prompt-answering quality. It is
not a personality detector, diagnostic tool, or claim that assessment results
reveal a fixed identity.

Hosting for real participants is planned in
`plans/17-validation-mvp-hosting.md`: Vercel may host the participant UI and
stateless API routes, but durable pilot data must use hosted Postgres or another
reviewed external datastore rather than local JSONDB files.

## MVP Flow

1. Operator shares one no-auth pilot link.
2. Participant opens the link and receives an opaque `participant_id`.
3. UI tells the participant to write down the ID for resume, export, or delete.
4. System presents a modular fictional scenario with:
   - participant role;
   - specified recipient;
   - context and tension;
   - concrete writing request;
   - bounded scenario description length.
5. Participant writes an organic response. Store it before assessment.
6. Participant completes an administrable assessment.
7. System derives assessment scores and provisional profile atoms.
8. System generates a predicted response to the same scenario using assessment
   outcomes, explicitly excluding the organic response.
9. System ranks both responses for how well they answer the prompt.
10. UI shows the predicted response and asks whether it sounds like the
    participant.
11. Participant selects alignment/misalignment reasons and may add correction
    text.
12. Store the difference as evaluation evidence for later modeling review.

## Scenario Contract

Scenarios are assembled from explicit modules, not freeform hidden prompts:

- `scenario_id`
- `version`
- `role`
- `recipient`
- `relationship`
- `situation`
- `stakes`
- `response_goal`
- `response_channel`
- `description_max_chars`
- `response_max_chars`

Initial limits:

- scenario description: 900 characters maximum;
- response request: 240 characters maximum;
- participant response: 2,000 characters maximum.

Allowed scenarios should be ordinary professional, creative, planning, or social
coordination situations. Exclude clinical, legal, financial, eligibility,
protected-trait, trauma, political-persuasion, and high-stakes safety contexts.

## Assessment Policy

Use existing administrable instruments only.

Default for the first real pilot:

- Mini-IPIP for a short but more informative OCEAN path.

Fallback for a very short smoke test:

- TIPI, with its existing diminished-precision caution.

Assessment-derived atoms remain provisional evidence. For this MVP, generation
uses a separate `assessment_prediction_context` packet scoped only to the
current scenario. The packet is a hypothesis source, not active global profile
state.

## Predicted Response Contract

The predicted response request must include:

- scenario ID/version and exact scenario text;
- assessment session ID and scoring/instrument fingerprint;
- assessment-derived candidate context;
- prompt/provider/application versions;
- explicit `organic_response_excluded: true`;
- request and context hashes;
- provider mode and model identifier when external generation is approved.

The request must not include the participant's organic response, raw assessment
item text beyond what is already required for scoring provenance, hidden
identity claims, or unrelated profile history.

## Ranking Contract

Rank prompt-answering quality separately from voice alignment.

Initial rubric:

- relevance to scenario;
- completeness of requested response;
- role and recipient fit;
- clarity and actionability;
- tone appropriateness for the situation.

Store rubric scores for both organic and predicted responses with method,
version, evaluator type, timestamp, and explanation. Do not use the ranking to
claim that one response is more authentically the participant.

## Alignment Feedback

After seeing the predicted response, ask:

- `sounds_like_me`: 1-5 scale;
- `would_send_or_edit`: send as-is, lightly edit, heavily edit, would not use;
- alignment reasons:
  - tone;
  - directness;
  - warmth;
  - structure;
  - word choice;
  - level of detail;
  - emotional register;
  - too generic;
  - too formal;
  - too casual;
  - too strong;
  - missing what I would say;
  - other;
- optional correction text.

Feedback updates a modeling-review queue or guidance mapping notes. It must not
silently rewrite assessment evidence, atom claims, confidence, or model weights.

## No-Auth Pilot Boundary

The link flow is for early validation only, not production security.

Requirements:

- unguessable pilot link;
- opaque participant ID;
- no email or account requirement;
- clear instruction that the ID is needed for resume/export/delete;
- no sensitive personal data requested;
- explicit provider disclosure before any external model call;
- export and delete by participant ID during the pilot.

For hosted pilots, the production participant route may be public. Access to a
participant's records depends on the high-entropy participant ID, not Vercel
login. Preview/admin surfaces should be protected separately.

## Implementation Increments

### Increment V0: Protocol And Copy

- [ ] Write participant consent, provider disclosure, and deletion copy.
- [ ] Define the first scenario module set.
- [ ] Define primary and secondary success metrics.
- [ ] Add unsafe-scenario review checklist.
- [ ] Confirm hosted pilot copy explains public link, participant ID, retention,
  export, delete, and any model-provider use.

Acceptance:

- a reviewer can run the study manually from the written protocol;
- no copy frames the system as mind-reading, diagnostic, or identity proof.

### Increment V1: Link, Participant ID, And Scenario Response

- [ ] Add no-auth pilot route.
- [ ] Create/store participant record with opaque ID.
- [ ] Present generated scenario and collect organic response.
- [ ] Export/delete participant records by ID.

Acceptance:

- participant can complete the pre-assessment scenario response;
- response is persisted with exact scenario provenance.

### Increment V2: Assessment And Candidate Context

- [ ] Administer Mini-IPIP or TIPI inside the pilot flow.
- [ ] Store assessment session and derive provisional atoms.
- [ ] Build scenario-scoped `assessment_prediction_context`.
- [ ] Keep derived atoms review-only unless explicitly reviewed later.

Acceptance:

- context packet is reproducible from the assessment session;
- broad traits are not promoted to active/global profile controls.

### Increment V3: Predicted Response And Ranking

- [ ] Generate predicted response from scenario plus candidate context.
- [ ] Prove organic response exclusion with a request-inspection test.
- [ ] Rank organic and predicted responses with the prompt-answering rubric.
- [ ] Persist request, output, ranking, and hashes.

Acceptance:

- predicted response is generated without prior response leakage;
- both responses have separate quality rankings.

### Increment V4: Alignment Feedback And Modeling Review

- [ ] Show predicted response and collect alignment feedback.
- [ ] Record structured reasons and optional correction text.
- [ ] Add local report of alignment, usefulness, and ranking distributions.
- [ ] Queue feedback for reviewed mapping/modeling updates.

Acceptance:

- feedback is bound to the exact participant, scenario, assessment context, and
  generated response;
- feedback does not mutate raw assessment evidence or profile claims.

## First Pilot Success Targets

Run only after deletion/export and provider disclosure are working.

Initial target:

- 5-8 consenting participants;
- at least 60% rate the predicted response `sounds_like_me >= 4`;
- median `would_send_or_edit` is send as-is or lightly edit;
- predicted prompt-answering quality is not materially worse than organic;
- every participant can explain that the output is a prediction attempt, not a
  personality fact;
- 100% successful participant export/delete checks.

These are product decision targets, not scientific validation claims.

## Deferred

- production authentication;
- multi-user account model;
- platform database migration;
- visual or moodboard inputs;
- experimental Sol OCEAN candidate activation;
- automatic model training;
- broad personality dashboards;
- high-stakes scenario categories.
