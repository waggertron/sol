# OCEAN Profile Atom Mapping v0

## Purpose

This document defines how OCEAN assessment results should become profile
evidence without turning broad trait scores into fixed identity labels.

## Mapping Rule

An assessment score should create or update a profile atom only as one evidence
source among others.

Preferred chain:

```text
assessment response -> construct score -> profile atom hypothesis -> user review
-> generation-scoped preference
```

Avoid:

```text
assessment response -> fixed user label -> global generation behavior
```

## Broad Trait Atom Template

```json
{
  "domain": "stable_trait_tendencies",
  "construct_family": "OCEAN",
  "trait": "openness",
  "facet_or_aspect": null,
  "claim": "User self-report suggests relatively high openness to experience.",
  "evidence_type": "self_report_assessment",
  "assessment_id": "ipip_big_five_family",
  "confidence": "medium",
  "stability": "stable_tendency",
  "context": "general_self_report",
  "user_visibility": "visible_editable",
  "generation_scope": "requires_task_specific_mapping"
}
```

## Generation Mapping Guidance

### Openness

Do:

- expose controls for novelty, abstraction, exploratory framing, and aesthetic
  complexity
- ask the user which implications are desired for the current task

Do not:

- assume high openness means the user always wants unusual output
- infer intelligence, education, politics, or mental health from openness

### Conscientiousness

Do:

- map to structure, completeness, sequencing, and planning detail
- distinguish useful organization from rigid overcontrol

Do not:

- infer work ethic from sparse data
- use conscientiousness for eligibility or employment decisions

### Extraversion

Do:

- map to energy level, social framing, assertiveness, and warmth
- allow task-specific toggles for private, professional, and public voice

Do not:

- assume introversion means low confidence or poor social skill
- force socially intense outputs when the task needs restraint

### Agreeableness

Do:

- map to tact, collaborative tone, critique style, and conflict handling
- allow directness controls because politeness preferences are contextual

Do not:

- infer compliance, gullibility, morality, or trustworthiness
- use agreeableness to steer covert persuasion

### Neuroticism / Negative Emotionality

Do:

- map carefully to reassurance, uncertainty handling, grounding, and stress-aware
  planning support when the user wants it
- prefer neutral language such as stress sensitivity or emotional reactivity in
  user-facing surfaces

Do not:

- present this trait as pathology
- infer diagnosis, impairment, instability, or risk status
- expose stigmatizing labels by default

## Minimum Safeguards

- User can inspect every assessment-derived atom.
- User can reject or edit trait implications.
- Trait atoms cannot be used in eligibility, diagnosis, or hidden profiling.
- Broad OCEAN scores must not directly control all outputs globally.
- Generation prompts should receive scoped implications, not raw trait labels,
  whenever possible.

