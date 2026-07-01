# Signal Matrix v0

This matrix maps possible user data sources to permissible inference levels.
It should be expanded as the research base grows.

## Inference Levels

- `observed`: directly present in the data
- `style_preference`: likely preference or habit for personalization
- `trait_hypothesis`: provisional personality interpretation
- `sensitive_hypothesis`: high-risk inference requiring opt-in or exclusion
- `blocked`: should not be inferred in this product context

## Writing Samples

Permissible:

- observed vocabulary, topics, structure, length, revision patterns
- communication style preferences
- provisional hypotheses about abstraction, directness, emotional tone, novelty,
  and social orientation

Cautions:

- a writing sample may reflect audience, genre, platform, or task rather than
  personality
- avoid inferring clinical status, protected traits, trauma history, or deception

## Chat History

Permissible:

- conversational pacing
- preferred depth
- formality
- correction patterns
- humor and directness preferences
- contexts where tone changes

Cautions:

- private conversations may include third-party data
- chats can reflect a local relationship dynamic, not a general trait

## Preference Ratings

Permissible:

- explicit likes, dislikes, and ranking behavior
- modality-specific style preferences
- changes over time

Cautions:

- preference is not personality
- novelty and fatigue can distort ratings

## Creative Artifacts

Permissible:

- genre, palette, composition, rhythm, texture, subject matter, and themes
- creative identity signals when user confirms them

Cautions:

- artifacts may be aspirational, commissioned, copied, or constrained by tools
- do not infer mental health state from aesthetic darkness or intensity

## Behavioral Telemetry

Permissible:

- product ergonomics
- feature preferences
- interaction friction
- generated-output selection patterns

Cautions:

- behavioral telemetry should default to preference and UX optimization
- personality inference from telemetry requires explicit consent and strong
  justification

## Direct Questionnaires

Permissible:

- self-reported traits
- explicit values
- declared goals
- preferred terms
- rejected interpretations

Cautions:

- questionnaires can be biased by self-presentation and current mood
- direct self-report should be combined with user-visible uncertainty, not
  treated as final truth

## Generation Feedback

Permissible:

- output-specific preferences
- corrections to profile atoms
- cross-modal style mappings

Cautions:

- a disliked output may reflect poor generation quality rather than inaccurate
  personality modeling

## Blocked or Highly Constrained Inferences

Default blocked:

- clinical diagnosis
- personality disorder labels
- protected class inference
- sexual orientation
- religious identity
- political persuasion targeting
- deception or criminality
- addiction or self-harm risk unless operating in a validated safety workflow

Default high sensitivity:

- trauma-related interpretations
- maladaptive personality extremes
- emotional instability claims
- honesty or exploitiveness claims
- attachment style claims
- intelligence or competence claims

