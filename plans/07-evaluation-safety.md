# Evaluation and Safety Plan

## Objective

Measure whether the system improves generation while preventing overclaiming,
hidden profiling, and unsafe use.

## Evaluation Questions

- Does the user recognize themselves in the profile?
- Do personalized outputs outperform generic outputs?
- Can users correct wrong inferences easily?
- Does trust increase or decrease over time?
- Which data sources produce useful signal?
- Which constructs are too noisy or risky?

## Candidate Metrics

- "feels like me" rating
- output usefulness rating
- forced-choice preference over generic baseline
- profile atom correction rate
- profile atom rejection rate
- confidence calibration
- longitudinal trust score

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

