# Knowledge Model v0

This document defines the first internal ontology for the RAG. It is not the
final user profile schema. It is the research map that lets us evaluate what
could responsibly become a profile schema.

## Top-Level Research Domains

### 1. Personality Structure

Purpose: model broad, relatively stable tendencies.

Candidate constructs:

- Big Five / Five-Factor Model
- HEXACO
- interpersonal circumplex
- cybernetic models of personality
- whole trait theory
- person-situation interaction models

RAG questions:

- Which traits have the strongest empirical support?
- Which traits are useful for generation?
- Which traits are too broad to control output directly?
- How do traits vary across contexts?

### 2. Personality Dynamics

Purpose: avoid treating personality as fixed averages only.

Candidate constructs:

- density distributions of states
- Cognitive-Affective Personality System (CAPS)
- if-then behavioral signatures
- trait-state distinction
- contextual modes

RAG questions:

- What changes across work, social, private, creative, and stress contexts?
- Can user data distinguish stable tendency from local state?
- How should the profile represent uncertainty and recency?

### 3. Psychometrics and Construct Validity

Purpose: prevent loose labels from becoming pseudo-measurement.

Candidate constructs:

- construct validity
- convergent validity
- discriminant validity
- test-retest reliability
- inter-rater reliability
- measurement invariance
- criterion validity
- ecological validity

RAG questions:

- What would count as evidence that a profile attribute is valid?
- How should inferred traits be calibrated against self-report?
- How do we avoid overfitting personality labels to sparse data?

Current implementation note:

- OCEAN assessment metadata and permissive/open instruments live under
  `assessments/ocean/`
- assessment-derived claims should be treated as self-report evidence, not
  final profile truth
- score-derived profile atoms should remain user-visible and editable

### 4. Language and Communication Signals

Purpose: infer style and possible trait signals from user-authored text.

Candidate evidence:

- function words and LIWC-style categories
- open-vocabulary topic clusters
- syntactic complexity
- sentiment and emotion words
- directness, hedging, politeness, humor, abstraction
- narrative perspective and temporal focus
- revision patterns

RAG questions:

- Which language signals are robust enough for personalization?
- Which signals are culturally or contextually fragile?
- How should the system separate writing style from personality claims?

### 5. Digital Behavior and Preference Signals

Purpose: use behavioral traces cautiously and with consent.

Candidate evidence:

- likes, saves, skips, ratings
- editing choices
- selection among generated variants
- browsing or media preference data, if explicitly authorized
- session behavior, where relevant

RAG questions:

- What can digital traces predict reliably?
- What should be treated as preference rather than personality?
- How do we prevent invasive inference from weak behavioral data?

### 6. Abnormal Psychology and Dimensional Psychopathology

Purpose: understand boundaries, not diagnose users.

Candidate frameworks:

- DSM-5 Alternative Model for Personality Disorders
- ICD-11 personality disorder trait qualifiers
- HiTOP
- RDoC

RAG questions:

- Which constructs describe maladaptive extremes of otherwise normal traits?
- Which product surfaces must avoid diagnosis-like language?
- How should the model represent distress, impairment, or risk without making
  clinical claims?

### 7. Affective and Motivational Systems

Purpose: capture why certain outputs resonate.

Candidate constructs:

- approach/avoidance motivation
- reward sensitivity
- threat sensitivity
- novelty seeking
- autonomy, competence, relatedness
- values and goals
- emotion regulation patterns

RAG questions:

- What motivational dimensions are useful for generation?
- How do motivational cues differ from stable personality traits?
- How can a user directly correct motivational interpretations?

### 8. Aesthetic and Creative Taste

Purpose: bridge personality signals to multimodal generation.

Candidate constructs:

- openness to experience and aesthetic engagement
- preference for complexity, symmetry, novelty, ambiguity
- color, texture, rhythm, density, symbolism, genre, era
- creative identity and taste communities

RAG questions:

- Which aesthetic preferences can be inferred from examples?
- How should visual, audio, and textual preferences share a common substrate?
- When is a preference merely task-specific?

### 9. Multimodal Generation Control

Purpose: map profile evidence into model instructions.

Candidate controls:

- tone
- pace
- abstraction level
- emotional intensity
- novelty
- structure
- density
- visual palette
- composition
- sound texture
- narrative arc
- interaction style

RAG questions:

- Which profile attributes map cleanly to generation controls?
- Which attributes should stay interpretive and not directly control output?
- How do we audit whether personalization improves output?

### 10. Ethics, Consent, and User Agency

Purpose: make the user model inspectable, reversible, and bounded.

Required capabilities:

- source-level provenance
- user-visible profile cards
- corrections and overrides
- deletion and export
- sensitive inference gating
- audit logs
- confidence labels
- context labels

RAG questions:

- What should the user always be able to inspect?
- How do we distinguish observed data from inferred interpretation?
- What categories should be blocked or opt-in only?

## Draft Engram Interpretation

"Engram" should be treated as a product metaphor unless we explicitly operate
inside neuroscience. In this project, it means:

> a durable, evidence-backed, user-correctable representation of patterns that
> help personalize future generation.

It does not mean:

- a literal memory trace in the brain
- a complete mind model
- a clinical personality diagnosis
- a fixed essence of the user

## Candidate Profile Atom

A profile atom is the smallest unit that might enter the user model.

Suggested fields:

- `id`
- `label`
- `domain`
- `claim`
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
- `generation_mappings`
- `counterevidence`
- `last_updated`

Example:

```json
{
  "id": "style.direct_low_fluff.v0",
  "label": "direct, low-fluff communication",
  "domain": "communication_style",
  "claim": "The user tends to prefer concise, concrete, action-oriented wording.",
  "evidence": ["User edits repeatedly removed hedging and long preambles."],
  "source_ids": ["user_revision_events"],
  "data_modality": "text",
  "context": ["work", "planning"],
  "confidence": 0.72,
  "stability": "medium",
  "recency": "last_30_days",
  "sensitivity_level": "low",
  "user_visibility": "visible_editable",
  "user_feedback": "unconfirmed",
  "generation_mappings": ["shorter introductions", "explicit next steps"],
  "counterevidence": [],
  "last_updated": "2026-07-01"
}
```
