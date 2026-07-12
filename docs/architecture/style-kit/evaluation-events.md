# Creative Style Kit Evaluation Events

## Scope

`tools/style_kit_evaluation.py` implements the local evaluation lifecycle for
persisted deterministic `mock://` pilot runs. It adds no routes, browser UI,
external provider, or automatic profile mutation.

An evaluation is user feedback about two outputs shown for one exact task. It
is not personality evidence, an identity fact, or a diagnostic result.

## Two-Step Blinded Lifecycle

Blinding is enforced through two persisted operations:

1. `record_blinded_choice` stores the presented variant IDs, their order, the
   opaque selected variant ID (or `tie`/`cannot_judge`), and the normalized UTC
   choice time. Variant identity has not yet been revealed and all feedback
   fields remain empty.
2. `reveal_and_record_feedback` can mutate only a `choice_recorded` event. The
   reveal time must be later than the stored choice time. Only then are the
   variant kind, optional ratings, labels, correction, and affected guidance
   treated as revealed feedback.

The service derives `personalized` or `generic` from the selected variant in
the persisted run. Callers cannot supply that mapping. A second reveal is
rejected.

## Eligibility And Integrity

Evaluation creation requires:

- a known, active, completed `mock://` run owned by the same user;
- exactly two distinct, passed, visible run outputs;
- a presentation order containing each run variant exactly once;
- consent references copied from the run; and
- affected guidance references limited to guidance actually used by the
  personalized variant.

`feels_like_me` and `usefulness` are optional integers from 1 through 5.
`wrong`, `too_strong`, and `too_generic` labels require correction text.
Evaluation writes do not modify sources, observations, profile atoms,
guidance, pilot runs, assessment responses, claims, or confidence.

## Deletion

An event can be independently deleted. Deletion preserves only the minimal
owner/run identity and lifecycle tombstone while clearing consent references,
presentation order, selection, ratings, labels, correction, affected guidance,
and choice/reveal timestamps. Other records are not changed.

## Storage And Validation

The service uses the contract-validating Style Kit repository. Tests select a
temporary database with `SOL_STYLE_KIT_DB`; the manual default remains the
ignored `tmp/style-kit/style-kit-records.json` path. Times must contain a
timezone and are normalized to second-precision UTC.

```bash
python3 -m unittest tests.test_style_kit_evaluation
python3 tools/validate_style_kit_contracts.py
./scripts/run_assessment_web_mvp_qa.sh
```

After manual local work, remove the ignored database if it was created:

```bash
rm -f tmp/style-kit/style-kit-records.json
```
