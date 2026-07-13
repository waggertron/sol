# Data and Consent Plan

## Objective

Define how the platform uses data with explicit permission, provenance,
inspection, correction, export, and deletion.

## Candidate Data Sources

- writing samples
- chat history
- journals
- social posts
- creative artifacts
- preference ratings
- output edits
- questionnaires and assessment responses
- visual/audio references

## Consent Requirements

- user knows which data sources are used
- user can see what each source contributed
- user can delete source data
- user can delete assessment responses separately from derived profile atoms
- user can delete derived profile atoms
- user can export profile data
- sensitive inferences are opt-in or blocked

## Participant-Link Pilot Requirements

For the no-auth validation MVP in
`plans/16-participant-link-validation-mvp.md`:

- use an unguessable pilot link and opaque participant ID;
- tell the participant to write down the ID for resume, export, and delete;
- do not request email, account creation, or sensitive personal data;
- store the fictional scenario, organic response, assessment references,
  predicted response, rankings, and feedback as separate exportable/deletable
  records;
- disclose any external model provider before generation;
- prove the organic response is excluded from the predicted-response request;
- treat alignment feedback as evaluation evidence, not automatic profile truth.

For hosted pilots, follow `plans/17-validation-mvp-hosting.md`: keep
participant access no-auth through an unguessable link and high-entropy
participant ID, but store durable pilot records in hosted Postgres rather than
local JSON files.

## Provenance Requirements

Every profile atom should be traceable to:

- data source
- evidence excerpt or feature
- inference method
- timestamp
- context
- confidence
- assessment and scoring version, when applicable

## Open Questions

- Should raw user data be stored, summarized, or processed ephemerally?
- How much evidence should be shown in the UI?
- What is the default retention period?
- How should third-party data inside chats be handled?
