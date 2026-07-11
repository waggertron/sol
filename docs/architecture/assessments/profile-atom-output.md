# Assessment Profile Atom Output

This document defines the first implementation-facing output contract for
assessment scoring.

It bridges:

- `assessments/ocean/instruments/*.json`
- `kb/assessments/ocean_profile_atom_mapping_v0.md`
- `kb/model/profile_atom_schema_v0.md`

## Goal

Assessment scoring should emit:

1. scored construct results
2. `provisional_atom` profile candidates

It should not emit globally active personalization controls directly.

## Output Rule

Every assessment-derived atom should:

- start as `state: "provisional_atom"`
- start as `activation_scope: "review_only"`
- remain `user_visibility: "visible_editable"`
- keep assessment provenance in `source_ids` and `assessment_metadata`
- initialize `original_claim` to the generated `claim`
- initialize `user_note` to an empty string and `review_history` to an empty list

User edits change `claim`, not `original_claim`. Review history is append-only,
and notes or edits must not alter raw assessment responses or derived scores.

## Current Generator

The first generator lives at:

- `tools/assessment_to_profile_atoms.py`

Current supported scoring methods:

- `sum_keyed_items`
- `average_two_items_per_domain`

Current intended first instruments:

- `assessments/ocean/instruments/tipi.json`
- `assessments/ocean/instruments/mini_ipip.json`

## Output Shape

Top-level output:

```json
{
  "assessment_id": "tipi",
  "assessment_name": "Ten Item Personality Inventory",
  "session_id": "session_001",
  "completed_at": "2026-07-08T00:00:00Z",
  "scores": [],
  "profile_atoms": []
}
```

Each profile atom follows `kb/model/profile_atom_schema_v0.md` and adds:

- `assessment_metadata.assessment_id`
- `assessment_metadata.assessment_name`
- `assessment_metadata.assessment_family`
- `assessment_metadata.construct_system`
- `assessment_metadata.scale_id`
- `assessment_metadata.scale_label`
- `assessment_metadata.trait`
- `assessment_metadata.score_type`
- `assessment_metadata.score_value`
- `assessment_metadata.score_range`
- `assessment_metadata.normalized_score`
- `assessment_metadata.session_id`

Scored results also retain inspectable calculation evidence:

- scoring method and interpretation
- raw and normalized score bounds
- reported reliability alpha when present in the stored instrument
- item id and text
- original response value
- positive or negative keying
- whether reverse scoring was applied
- the keyed value used in the calculation

The same item evidence, instrument notes, license posture, source link, and
uncertainty copy are copied into `assessment_metadata` so an exported or
cross-session atom remains explainable without recomputing the session.

## Implementation Policy

- assessment results are self-report evidence, not identity facts
- broad OCEAN traits remain candidates until user review
- neuroticism / emotional stability should use non-diagnostic language
- generation systems should consume only atoms that have been promoted beyond
  `review_only`
- reliability is presented as prior score-consistency evidence, not proof that
  an individual claim is true
- TIPI results carry an explicit diminished-precision caution because the
  instrument is intentionally very brief

## Example Command

```bash
python3 tools/assessment_to_profile_atoms.py \
  --instrument assessments/ocean/instruments/tipi.json \
  --responses /path/to/tipi_responses.json \
  --session-id session_001 \
  --completed-at 2026-07-08T00:00:00Z
```
