# First Wedge Plan: Personal Creative Style Kit

## Wedge Statement

Create a Personal Creative Style Kit that turns user-provided data into an
editable personality/style profile, then generates text and visual direction
that the user can evaluate.

Current implementation note: the assessment-first step is complete through
editable atoms, evidence views, and scoped context export. Domain-level guidance
persisted dry-run/mock pilot provenance, and run-bound blinded evaluation are
also complete. The remaining wedge work begins with browser surfaces, then
consented writing/preference inputs before visual expansion.

Current validation shortcut: before building the full Style Kit surface, build
the participant-link scenario MVP in `plans/16-participant-link-validation-mvp.md`.
It tests whether an assessment-informed predicted response to a fictional
scenario sounds like the participant, while storing the participant's organic
response only for comparison and never using it as generation input.

## Why This Wedge

- It exercises the complete platform loop.
- It has useful personality, communication, and aesthetic signals.
- It avoids high-risk eligibility or diagnosis contexts.
- Outputs are easy for users to judge.
- It can expand into text, image, audio, avatar, video, and agent behavior.

## MVP Inputs

- no-auth shared pilot link and opaque participant ID
- modular fictional scenario with a specific recipient and writing request
- one organic participant response
- short administrable assessment from `assessments/ocean/`
- alignment/misalignment feedback on the predicted response
- direct correction text

## MVP Profile Outputs

- communication style summary
- aesthetic preference summary
- motivational and value hypotheses
- creative pattern observations
- confidence and evidence per profile atom
- editable user-facing profile cards

## MVP Generated Outputs

- predicted response to the same scenario, using assessment-derived candidate
  context and excluding the organic response
- prompt-answering quality rankings for organic and predicted responses

Later Style Kit outputs can include a short bio, writing voice guide, project
description, content ideas, image-prompt directions, and visual moodboard
description after the validation shortcut is interpretable.

## Required Feedback

- profile atom confirm/edit/reject
- output rating
- "feels like me" rating
- "useful" rating
- direct correction text

## Expansion Paths

- writing assistant
- visual identity generator
- avatar or persona builder
- music/audio direction
- adaptive AI companion behavior
- API profile layer
