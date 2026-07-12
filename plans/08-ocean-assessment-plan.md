# OCEAN Research, Assessment, and MVP Plan

## Objective

Start assessment gathering with the Big Five / OCEAN trait layer:

- Openness to Experience
- Conscientiousness
- Extraversion
- Agreeableness
- Neuroticism / Negative Emotionality / Emotional Stability

The goal is not to pick a personality test and treat it as ground truth. The
goal is to build a legally usable, psychometrically defensible assessment layer
that can calibrate profile atoms, provide user-visible self-report anchors, and
evaluate whether passive or generative signals are aligned with validated trait
constructs.

This plan has four phases:

1. Gather OCEAN research.
2. Gather OCEAN assessments.
3. Analyze research, assessments, and question patterns to design original Sol
   assessment candidates that can be administered and scored.
4. Build an MVP web app for administration, result storage, scoring, and score
   presentation.

Current state: Phase 2 has an initial acquisition complete for permissive/open
instruments. `assessments/ocean/manifest.json` currently tracks 11 instruments,
186 scales, and 1,539 items. Phase 4 is complete as a local prototype. Phase 3
now has a design-review-only construct blueprint, item-writing contract, and
30-item `Sol-OCEAN-Quick-v0` candidate outside the administrable manifest.
Independent expert review, cognitive interviews, and empirical validation
remain open in `plans/13-sol-ocean-experimental-assessment.md`.

## Working Principles

- Do not copy protected test items into the repo unless the instrument license
  clearly permits it.
- Prefer public-domain or explicitly reusable instruments for product
  prototypes.
- Treat proprietary and clinical inventories as reference-only unless a license
  and professional-use review says otherwise.
- Use broad OCEAN traits as organizing categories, not direct generation
  controls.
- Map generation behavior from facets, aspects, observed behaviors, and user
  corrections before broad trait scores.
- Preserve uncertainty, context, recency, and source provenance for every
  assessment-derived profile atom.
- Treat any Sol-created assessment as experimental until reliability, validity,
  measurement invariance, and user comprehension have been tested.

## Phase 1: Gather OCEAN Research

Purpose: build the theoretical and psychometric foundation for OCEAN before
choosing or designing any assessment items.

Research targets:

- lexical hypothesis and Big Five trait structure
- Five-Factor Model facet structure
- Big Five Inventory-2 15-facet hierarchy
- Big Five Aspects Scale 10-aspect hierarchy
- cybernetic interpretations of Big Five traits
- whole trait theory and trait/state density distributions
- stability and change across time
- measurement reliability and validity
- self-report limitations, response bias, and faking
- cross-cultural and language measurement invariance
- ethical limits around trait interpretation

Outputs:

- source registry entries for OCEAN papers
- source cards for high-value papers
- trait/facet/aspect crosswalk
- contraindication notes for weak or risky inferences
- research-backed definitions suitable for user-facing language

Acceptance criteria:

- Each OCEAN domain has a definition, lower-level constructs, likely evidence
  sources, and known interpretation risks.
- Each candidate construct has at least one primary or high-quality secondary
  source.
- RAG retrieval can answer "what supports this OCEAN construct?" and "what are
  the cautions?"

## Phase 2: Gather OCEAN Assessments

Purpose: inventory existing OCEAN instruments, determine legal/product posture,
and decide what can be used for prototypes or reference.

Assessment targets:

- IPIP Big Five and IPIP-NEO representations
- Ten Item Personality Inventory
- Big Five Inventory-2 family
- Big Five Aspects Scale
- BFI-10
- NEO PI-R / NEO-PI-3 / NEO-FFI as reference-only unless licensed
- HEXACO-PI-R as adjacent comparison, not strict OCEAN

For each assessment, capture:

- instrument name
- construct family
- domains and facets/aspects measured
- item count and administration burden
- scoring method availability
- item text storage permission
- commercial/product permission posture
- validation sources
- translation availability
- known psychometric weaknesses
- whether it is usable now, needs license review, or is reference-only

Outputs:

- `jsondb/assessment_inventory.json`
- `assessments/ocean/manifest.json`
- `assessments/ocean/instruments/*.json`
- `kb/assessments/ocean_assessment_catalog_v0.md`
- import queue entries for missing validation papers
- license review queue for instruments with uncertain permissions

Acceptance criteria:

- At least one permissive OCEAN instrument is selected for prototype use.
- Strong reference instruments are cataloged without copying protected items.
- The project can explain why an instrument is usable, blocked, or reference
  only.

## Phase 3: Design Original Sol OCEAN Assessment Candidates

Purpose: use the research and assessment inventory to create original Sol
assessment candidates that can eventually be administered and scored without
copying protected instruments.

This phase must be framed as experimental instrument development, not as the
creation of an already validated personality test.

Method:

1. Build a construct blueprint for each OCEAN domain and lower-level
   facet/aspect.
2. Compare how existing instruments operationalize each construct without
   copying protected wording.
3. Generate an original item pool for each construct.
4. Label every item by target construct, reverse-key status, reading level,
   sensitivity, and expected failure mode.
5. Review items for ambiguity, leading wording, cultural loading, social
   desirability, and overlap with clinical/pathology language.
6. Pilot the item pool internally or with consenting testers.
7. Estimate internal consistency, factor structure, test-retest reliability, and
   convergent validity against a permissive benchmark such as IPIP.
8. Remove or rewrite weak items.
9. Freeze a named experimental form only after scoring and interpretation are
   documented.

Candidate Sol assessment forms:

- `Sol-OCEAN-Quick`: short onboarding form for broad trait estimates.
- `Sol-OCEAN-Facet`: longer form for product calibration and generation mapping.
- `Sol-OCEAN-State`: repeated lightweight form for current context and trait
  expression.
- `Sol-Style-Bridge`: maps OCEAN-relevant patterns to communication and
  creative generation preferences.

Scoring requirements:

- raw score
- normalized score within the form
- confidence based on item count, consistency, and missingness
- uncertainty text for user presentation
- no diagnosis or eligibility language
- user correction and override support

Outputs:

- original item pool stored only after review
- scoring specification
- interpretation guide
- validation backlog
- assessment-to-profile atom mapping

Acceptance criteria:

- Every generated item traces to a construct blueprint and does not copy a
  protected instrument.
- Every score has an uncertainty label and a user-visible explanation.
- No Sol assessment is described as validated until empirical validation exists.

## Phase 4: MVP Web App

Purpose: administer selected OCEAN assessments, store responses and results,
score submissions, and present results to users in a clear, editable,
non-diagnostic way.

MVP capabilities:

- assessment catalog page
- consent screen before administration
- questionnaire administration UI
- autosave and resume
- response storage
- scoring engine
- score result storage
- user-facing results presentation
- profile atom generation from scores
- edit/reject/correct controls for generated profile atoms
- export and deletion controls
- admin view for instrument versions and scoring specs

Core entities:

- `assessment`
- `assessment_version`
- `assessment_item`
- `assessment_response_session`
- `assessment_response`
- `assessment_score`
- `profile_atom`
- `profile_atom_evidence`
- `user_correction`

Scoring flow:

1. User consents to an assessment.
2. App creates an assessment response session.
3. User submits item responses.
4. Scoring engine validates completion and scoring version.
5. Scoring engine computes trait/facet/aspect scores.
6. App stores raw responses separately from derived scores.
7. App creates assessment-derived profile atom candidates.
8. User reviews result summaries and confirms, edits, or rejects profile atoms.

Result presentation:

- show plain-language trait descriptions
- show uncertainty and "what this does not mean"
- show likely generation implications as editable controls
- avoid stigmatizing labels, especially for Neuroticism / Negative Emotionality
- explain that assessment results are self-report signals, not fixed facts

Initial app scope:

- single-user local or simple hosted MVP
- one permissive assessment first, likely IPIP or TIPI
- versioned scoring spec
- JSON or lightweight database storage at first
- no clinical, employment, or eligibility use cases

Acceptance criteria:

- A user can complete an OCEAN assessment end to end.
- Responses and scores are stored with assessment version provenance.
- The app can regenerate scores from stored responses and scoring spec.
- The user sees editable, non-diagnostic results.
- Assessment-derived profile atoms can be exported for later generation tests.

## Immediate Assessment Tiers

### Tier 1: Usable Now

- IPIP Big Five and IPIP-NEO representations.
- TIPI as a very short onboarding or smoke-test measure.

These are useful for prototypes because they have permissive use postures. TIPI
should be treated as a coarse signal only because very short scales trade
precision for speed.

### Tier 2: Candidate With License Review

- Big Five Inventory-2 family.
- Big Five Aspects Scale.
- BFI-10.
- HEXACO-PI-R as an adjacent six-factor model.

These are strong psychometric references but need item, scoring, translation,
and commercial-use review before product inclusion.

### Tier 3: Reference-Only Unless Licensed

- NEO PI-R, NEO-PI-3, and NEO-FFI.
- MMPI, PAI, and other clinical or psychopathology instruments.

These may inform construct boundaries, validity expectations, and risk controls,
but should not be administered or reproduced by the product without appropriate
license and professional review.

## OCEAN Trait Crosswalk

### Openness

Candidate lower-level constructs:

- aesthetic sensitivity
- intellectual curiosity
- creative imagination
- openness to ideas
- novelty and complexity preference
- tolerance for ambiguity

Possible generation implications:

- novelty level
- conceptual abstraction
- metaphor and symbolism density
- visual complexity
- genre range
- exploratory versus conventional framing

### Conscientiousness

Candidate lower-level constructs:

- organization
- productiveness or industriousness
- responsibility
- orderliness
- deliberation
- persistence

Possible generation implications:

- structure and sequence
- completeness
- planning detail
- actionability
- precision
- risk of over-rigidity in generated output

### Extraversion

Candidate lower-level constructs:

- sociability
- assertiveness
- energy level
- enthusiasm
- positive emotionality
- social reward orientation

Possible generation implications:

- interpersonal warmth
- assertive versus reserved tone
- energetic pacing
- direct calls to action
- social framing
- presentation intensity

### Agreeableness

Candidate lower-level constructs:

- compassion
- respectfulness or politeness
- trust
- cooperation
- conflict aversion or conflict style
- prosocial orientation

Possible generation implications:

- collaborative tone
- warmth and tact
- conflict handling
- directness boundaries
- supportiveness
- critique style

### Neuroticism / Negative Emotionality

Candidate lower-level constructs:

- anxiety
- emotional volatility
- withdrawal
- stress sensitivity
- vulnerability under pressure
- mood reactivity

Possible generation implications:

- reassurance level
- uncertainty framing
- emotional intensity
- risk-sensitive language
- grounding and planning support
- avoid diagnostic or pathology-like claims

## Data Model Work

Add an OCEAN assessment source as a profile evidence source, not as a profile
identity.

Minimum profile atom fields for assessment evidence:

- `assessment_id`
- `construct`
- `trait_domain`
- `facet_or_aspect`
- `score_type`
- `score_value`
- `score_range`
- `norm_reference`
- `administration_context`
- `date_collected`
- `license_posture`
- `confidence`
- `user_visible_summary`
- `user_correction_state`

## First Implementation Sequence

1. Use IPIP or TIPI for an internal prototype assessment path.
2. Build an assessment inventory JSONDB with source, construct, license posture,
   scoring status, and product suitability.
3. Add OCEAN profile atom templates that distinguish broad trait, facet/aspect,
   and generation-control mapping.
4. Create a self-report calibration flow with explicit consent and correction.
5. Compare assessment results with writing-sample and preference-derived
   hypotheses, but do not overwrite user corrections.
6. Build an evaluation set for whether OCEAN-derived context improves output
   usefulness and "feels like me" ratings.

## Open Questions

- Should the MVP use a very short instrument for onboarding or a longer
  instrument for better facet-level calibration?
- Should OCEAN results be shown as trait labels, facet cards, or generation
  preference controls?
- What language should the UI use for Neuroticism / Negative Emotionality so it
  is useful without feeling pathologizing?
- Should broad scores ever be visible, or should users primarily see editable
  implications?
- Which assessment sources can be used commercially without extra licensing?
