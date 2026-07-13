# Writing And Communication Guide Pilot

## Purpose

Exercise the first `assess -> inspect -> correct -> use` handoff without making
an external model call. The pilot renders the exact prompt and eligible scoped
profile context intended for a future writing and communication style guide.

## Safety Contract

- Consume only packet atoms with `eligible_for_generation: true`.
- Describe profile context as tentative, user-correctable guidance.
- Do not diagnose or infer protected traits, intelligence, morality,
  competence, or mental health.
- Keep contextual evidence scoped to matching uses.
- Preserve self-report uncertainty and contraindications.
- Turn atoms without concrete generation guidance into questions rather than
  inventing style rules.

## Dry Run

At least one atom must first have `confirmed` or `edited` feedback, be promoted
to `active_atom` with `contextual` or `global` activation scope, and have a
non-blocked sensitivity level.

```bash
python3 tools/generation_pilot.py \
  --pilot-id writing_guide_001 \
  --generated-at 2026-07-11T00:00:00Z
```

Optional manual-review output must stay under the ignored feature directory:

```bash
python3 tools/generation_pilot.py \
  --pilot-id writing_guide_001 \
  --generated-at 2026-07-11T00:00:00Z \
  --output tmp/generation-pilot/writing-guide-dry-run.json
```

Cleanup only this pilot's local artifacts with:

```bash
rm -rf tmp/generation-pilot
```

## Current Boundary

`external_model_called` is always `false`. A model-backed mode remains blocked
until the prompt and feedback contracts have been reviewed together.

The participant-link validation MVP defines a separate predicted-response
pilot path. That path may later request a narrow provider gate for one scenario
response task, but it must preserve explicit provider disclosure, bounded
assessment-prediction context, and proof that the participant's organic
response was excluded from generation input.

The dry run separates the system instruction from a JSON user payload. The
system instruction explicitly treats every profile-context field as quoted
data and ignores commands embedded in user-edited claims or notes.

## Feedback Capture

Feedback values are `accurate`, `useful`, `too_strong`, `too_generic`, or
`wrong`. Each event references atoms as `session_id::atom_id` so repeated
assessment atom ids remain unambiguous across sessions.

```bash
python3 tools/assessment_session_store.py record-generation-feedback \
  --event-id feedback_001 \
  --pilot-id writing_guide_001 \
  --recorded-at 2026-07-11T00:05:00Z \
  --feedback too_generic \
  --atom-ref 'session_001::assessment.tipi.tipi_extraversion.v0' \
  --note "Ask about professional versus social voice."
```

Feedback appends an inspectable `generation_mapping_notes` entry and provenance
source id. It does not automatically change raw responses, the atom claim, or
confidence.

Negative feedback (`too_strong`, `too_generic`, or `wrong`) requires an
explanatory note. Duplicate atom references and feedback for atoms that are not
currently generation-eligible are rejected.
