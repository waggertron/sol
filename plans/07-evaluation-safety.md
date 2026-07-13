# Evaluation and Safety Plan

## Objective

Measure whether the system improves generation while preventing overclaiming,
hidden profiling, and unsafe use.

## Evaluation Questions

- Does the user recognize themselves in the profile?
- Do personalized outputs outperform generic outputs?
- Does an assessment-informed predicted response sound like the participant
  when the participant's prior organic response is excluded from generation?
- Does the predicted response answer the scenario prompt well enough to be
  useful, independent of voice alignment?
- Can users correct wrong inferences easily?
- Does trust increase or decrease over time?
- Which data sources produce useful signal?
- Which constructs are too noisy or risky?
- Do self-report assessment scores produce useful, user-accepted profile atom
  candidates?

## Candidate Metrics

- "feels like me" rating
- output usefulness rating
- forced-choice preference over generic baseline
- predicted-response sounds-like-me rating
- would send as-is / lightly edit / heavily edit / not use
- organic versus predicted prompt-answering rubric score
- profile atom correction rate
- profile atom rejection rate
- confidence calibration
- longitudinal trust score
- assessment completion rate
- score regeneration consistency
- assessment-derived profile atom confirmation/rejection rate

## Safety Boundaries

Blocked:

- diagnosis
- eligibility decisions
- protected-class inference
- hidden profiling
- covert political persuasion
- clinical personality disorder labeling

High-sensitivity:

- trauma-related interpretations
- emotional instability
- honesty/exploitiveness
- attachment style
- intelligence or competence

## Review Checklist

- Is the claim supported by evidence?
- Is the user allowed to inspect and correct it?
- Is the attribute necessary for generation?
- Is the attribute sensitive?
- Is the context clearly scoped?
- Is confidence visible internally, and where useful, externally?
- Can the user delete assessment responses separately from derived profile atoms?
- For participant-link pilots, can the user export or delete all records by the
  opaque participant ID?
- Does request inspection prove the predicted response excluded the organic
  participant response?
