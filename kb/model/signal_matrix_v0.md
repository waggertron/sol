# Signal Matrix v0

This matrix maps possible user data sources to permissible inference levels.
It should be expanded as the research base grows.

## Inference Levels

- `observed`: directly present in the data
- `candidate_atom`: aggregated cue with some interpretive structure, but not
  yet approved for downstream generation control
- `style_preference`: likely preference or habit for personalization
- `trait_hypothesis`: provisional personality interpretation
- `sensitive_hypothesis`: high-risk inference requiring opt-in or exclusion
- `blocked`: should not be inferred in this product context

Operational note:

- `observed` and `candidate_atom` data may be stored for retrieval and audit.
- Only sufficiently supported, low-risk, and where appropriate user-confirmed
  candidates should be promoted into active generation-steering atoms.
- This thresholding rule is informed by
  `kb/cards/dehaene_workspace_neuroscience.md` and
  `kb/cards/baars_global_workspace_theory.md`.

## Writing Samples

Permissible:

- observed vocabulary, topics, structure, length, revision patterns
- candidate atoms for recurring discourse style patterns
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
- candidate atoms for mode shifts such as planning mode, reflective mode, or
  exploratory ideation mode

Cautions:

- private conversations may include third-party data
- chats can reflect a local relationship dynamic, not a general trait

## Preference Ratings

Permissible:

- explicit likes, dislikes, and ranking behavior
- modality-specific style preferences
- changes over time
- evidence for promotion or suppression of existing preference atoms

Cautions:

- preference is not personality
- novelty and fatigue can distort ratings

## Creative Artifacts

Permissible:

- genre, palette, composition, rhythm, texture, subject matter, and themes
- creative identity signals when user confirms them
- contextual candidate atoms for visual or expressive mode

Cautions:

- artifacts may be aspirational, commissioned, copied, or constrained by tools
- do not infer mental health state from aesthetic darkness or intensity

## Behavioral Telemetry

Permissible:

- product ergonomics
- feature preferences
- interaction friction
- generated-output selection patterns
- repeated evidence about when a candidate atom should become active or remain
  context-bound

Cautions:

- behavioral telemetry should default to preference and UX optimization
- personality inference from telemetry requires explicit consent and strong
  justification
- telemetry alone should rarely promote a broad trait claim into a global
  active atom

## Direct Questionnaires

Permissible:

- self-reported traits
- OCEAN assessment responses and score results from stored permissive/open
  instruments
- explicit values
- declared goals
- preferred terms
- rejected interpretations

Cautions:

- questionnaires can be biased by self-presentation and current mood
- direct self-report should be combined with user-visible uncertainty, not
  treated as final truth
- assessment item text, scoring, and norms should be stored only when the source
  is public-domain, explicitly permissive, or otherwise approved
- self-report can justify promotion of a candidate atom, but should still remain
  user-editable and context-aware

## Generation Feedback

Permissible:

- output-specific preferences
- corrections to profile atoms
- cross-modal style mappings
- direct evidence for activating, scoping, or suppressing existing atoms

Cautions:

- a disliked output may reflect poor generation quality rather than inaccurate
  personality modeling

## Activation Rule

Use the signal matrix to decide not only whether an inference is permissible,
but also whether it is:

- retrievable only
- candidate-only
- context-active
- globally active

Default rule:

- broad trait and motivational claims stay candidate-only until there is
  repeated evidence or user confirmation
- direct style preferences can become context-active earlier
- high-sensitivity claims should never become globally active without an
  explicit, validated reason, and most should remain blocked

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
