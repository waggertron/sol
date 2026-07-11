# Profile Atom Schema v0

This document defines the first concrete contract for profile atoms that move
from research model to product implementation.

It is intentionally stricter than the high-level ontology in
`kb/model/knowledge_model_v0.md`.

## Purpose

The schema exists to preserve four distinctions:

1. observation versus interpretation
2. candidate versus active atom
3. context-bound use versus global use
4. model inference versus user-confirmed profile state

## Required Fields

- `id`
- `label`
- `domain`
- `claim`
- `original_claim`
- `state`
- `activation_scope`
- `evidence`
- `source_ids`
- `data_modality`
- `context`
- `confidence`
- `stability`
- `recency`
- `sensitivity_level`
- `user_visibility`
- `user_feedback`
- `user_note`
- `review_history`
- `generation_mappings`
- `counterevidence`
- `last_updated`

## Field Definitions

### `id`

Stable identifier for the atom.

Example:

```text
style.direct_low_fluff.v0
```

### `label`

Short user-facing or internal title.

### `domain`

High-level category. Prefer existing ontology domains.

Examples:

- `communication_style`
- `stable_trait_tendencies`
- `context_specific_states`
- `motivational_patterns`
- `aesthetic_creative_preferences`

### `claim`

Plain-language statement of what the atom means.

This should be interpretable and auditable. Avoid clinical or neuroscientific
language unless the source explicitly warrants it and the product allows it.

### `original_claim`

Immutable generated claim captured when the atom is created. User edits update
`claim` but must not overwrite `original_claim`.

### `state`

Lifecycle position of the atom.

Allowed values:

- `observed_candidate`
- `provisional_atom`
- `active_atom`
- `suppressed_atom`

Guidance:

- `observed_candidate`: extracted cue or localized pattern
- `provisional_atom`: aggregated interpretation ready for review or display
- `active_atom`: confirmed or sufficiently supported atom allowed to influence
  generation
- `suppressed_atom`: stale, contradicted, user-rejected, or out-of-scope atom

### `activation_scope`

Controls where the atom may influence downstream generation.

Allowed values:

- `review_only`
- `contextual`
- `global`

Guidance:

- `review_only`: retrievable for audit or explanation only
- `contextual`: active only in matching contexts
- `global`: eligible across most product contexts

### `evidence`

List of concise evidence statements.

Examples:

- repeated user edits removing filler
- strong preference ratings for concise outputs
- TIPI extraversion responses with moderate consistency

### `source_ids`

List of provenance pointers. These can reference:

- assessment results
- chat sessions
- feedback events
- imported source cards
- uploaded artifacts

### `data_modality`

One or more modalities that produced the evidence.

Examples:

- `text`
- `assessment`
- `ratings`
- `image`
- `audio`
- `interaction`

### `context`

Contexts where the atom was observed or should apply.

Examples:

- `general`
- `work`
- `planning`
- `creative`
- `reflective`
- `social`

### `confidence`

Normalized confidence score for the current claim.

Initial convention:

- `0.0` to `1.0`

This is an operational confidence field, not a scientific certainty claim.

### `stability`

Expected persistence of the atom.

Suggested values:

- `low`
- `medium`
- `high`

### `recency`

How recently the supporting evidence was updated.

Suggested representation:

- coarse label for UI, such as `last_7_days`, `last_30_days`, `historical`
- or a structured timestamp window in implementation

### `sensitivity_level`

Risk category for handling and presentation.

Suggested values:

- `low`
- `medium`
- `high`
- `blocked`

### `user_visibility`

How inspectable the atom is to the user.

Suggested values:

- `visible_editable`
- `visible_read_only`
- `internal_review_only`

Default target for ordinary profile atoms: `visible_editable`.

### `user_feedback`

Current user relationship to the claim.

Suggested values:

- `unconfirmed`
- `confirmed`
- `edited`
- `rejected`

### `user_note`

Optional user-authored context, correction, or qualification. Notes do not
modify raw evidence or assessment responses.

### `review_history`

Append-only list of material review changes. Each entry records `reviewed_at`
and field-level `from` / `to` values for changes to claim, note, feedback,
lifecycle state, or activation scope. No-op reviews do not add history.

### `generation_mappings`

List of downstream personalization effects that this atom may support.

Examples:

- shorter introductions
- explicit next steps
- lower ornamentation
- more exploratory ideation

### `counterevidence`

List of observations that weaken or constrain the claim.

Examples:

- user prefers dense prose in reflective writing
- trait-like signal appears only in work context

### `last_updated`

Timestamp of last material atom update.

## Promotion Rules

Default progression:

1. raw signal creates `observed_candidate`
2. repeated evidence creates `provisional_atom`
3. user confirmation or strong repeated evidence may create `active_atom`
4. contradiction, staleness, or rejection creates `suppressed_atom`

## Activation Rules

Default policy:

- broad trait claims should not become `global` without repeated evidence or
  user confirmation
- style preferences may become `contextual` earlier than trait hypotheses
- sensitive or ambiguous claims should remain `review_only` or be blocked

## MVP Guidance

For the assessment-first MVP:

- assessment score outputs should generally start as `provisional_atom`
- user review should determine whether they remain contextual, become global,
  or are rejected
- generation should consume only atoms that are not `suppressed_atom` and are
  not `review_only`

## Example

```json
{
  "id": "style.direct_low_fluff.v0",
  "label": "direct, low-fluff communication",
  "domain": "communication_style",
  "original_claim": "User prefers concise, concrete, action-oriented wording.",
  "claim": "User prefers concise, concrete, action-oriented wording.",
  "state": "active_atom",
  "activation_scope": "global",
  "evidence": [
    "User edits repeatedly removed hedging and long preambles.",
    "Positive ratings on concise assistant outputs."
  ],
  "source_ids": [
    "chat_session_12",
    "generation_feedback_batch_4"
  ],
  "data_modality": [
    "text",
    "ratings"
  ],
  "context": [
    "general",
    "work",
    "planning"
  ],
  "confidence": 0.72,
  "stability": "medium",
  "recency": "last_30_days",
  "sensitivity_level": "low",
  "user_visibility": "visible_editable",
  "user_feedback": "confirmed",
  "user_note": "Especially for work and planning.",
  "review_history": [],
  "generation_mappings": [
    "shorter introductions",
    "explicit next steps"
  ],
  "counterevidence": [
    "Prefers more descriptive language in reflective writing."
  ],
  "last_updated": "2026-07-08T00:00:00Z"
}
```
