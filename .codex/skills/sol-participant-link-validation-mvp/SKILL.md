---
name: sol-participant-link-validation-mvp
description: Use when planning, implementing, reviewing, or testing the Sol participant-link voice validation MVP, including no-auth pilot links, participant IDs, modular fictional scenarios, organic response capture, assessment-informed predicted responses, prompt-answering ranking, and alignment feedback.
---

# Sol Participant Link Validation MVP

## Overview

Use this skill for the fast real-user validation slice documented in
`plans/16-participant-link-validation-mvp.md` and
`docs/adr/2026-07-13-participant-link-validation-mvp.md`.

The MVP tests whether an assessment-informed predicted response to a fictional
scenario sounds like the participant. It must not frame the system as a true
personality detector, diagnostic tool, or fixed identity model.

## Required Context

Before substantial work, read:

- `docs/project-memory.md`
- `docs/current-state.md`
- `plans/16-participant-link-validation-mvp.md`
- `docs/adr/2026-07-13-participant-link-validation-mvp.md`

When assessment-derived atoms or profile context are touched, also read:

- `kb/model/profile_atom_schema_v0.md`
- `docs/architecture/assessments/profile-atom-output.md`
- `docs/architecture/assessments/session-storage.md`
- `docs/architecture/assessments/generation-contract-review.md`

## Workflow

1. Preserve the no-auth pilot boundary: use an unguessable link and opaque
   participant ID, with no account or email requirement.
2. Tell the participant to write down the ID for resume, export, or delete.
3. Present a modular fictional scenario with a specific role, recipient,
   situation, writing request, and explicit character limits.
4. Store the participant's organic response before assessment.
5. Administer only an existing manifest-approved assessment. Do not activate the
   experimental Sol OCEAN candidate.
6. Generate the predicted response from the same scenario plus
   assessment-derived candidate context.
7. Prove the organic response is excluded from the predicted-response request.
8. Rank organic and predicted responses for prompt-answering quality separately
   from voice alignment.
9. Ask whether the predicted response sounds like the participant and collect
   structured alignment or misalignment reasons.
10. Store feedback as evaluation evidence or mapping-review input; do not
   silently mutate assessment responses, profile claims, confidence, or model
   weights.

## Safety Gates

- Use ordinary professional, creative, planning, or social coordination
  scenarios only.
- Exclude clinical, legal, financial, eligibility, protected-trait, trauma,
  political-persuasion, and high-stakes safety contexts.
- Treat assessment outputs as self-report evidence and provisional candidate
  context, not identity facts.
- Require explicit provider disclosure before any external model call.
- Keep mock and dry-run paths available for automated tests.
- Ensure participant export/delete covers scenario, organic response,
  assessment references, predicted response, rankings, and feedback.
