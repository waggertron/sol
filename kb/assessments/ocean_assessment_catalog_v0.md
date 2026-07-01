# OCEAN Assessment Catalog v0

## Purpose

This catalog tracks assessment instruments relevant to the OCEAN / Big Five
layer. It is a decision aid for product and research planning, not a repository
of questionnaire items.

The project should store instrument metadata, scoring concepts, source links,
and licensing posture before storing any actual item text.

## Stored Assessment Area

Full item and scoring data that is currently permitted for repo storage lives in
`assessments/ocean/`.

The acquisition manifest is:

- `assessments/ocean/manifest.json`

Current stored instruments include IPIP Big Five factor markers, Mini-IPIP,
Mini-IPIP6, IPIP Big Five Aspects, IPIP AB5C facets, IPIP NEO domain and facet
representations, IPIP-NEO-120 variants, IPIP-NEO-60, and TIPI.

## Use Posture Legend

- `usable_now`: appears suitable for prototype use based on current public
  source language.
- `license_review`: potentially useful, but requires item/scoring/commercial-use
  review before product use.
- `reference_only`: use for construct grounding and comparison only unless a
  license and qualified review permit administration.
- `blocked_for_product`: should not be used in this project surface without a
  major product, clinical, and legal change.

## Candidate Instruments

### IPIP Big Five / IPIP-NEO Representations

Assessment id: `ipip_big_five_family`

Primary constructs:

- Big Five broad traits
- Big Five facets, depending on selected IPIP representation

Use posture: `usable_now`

Why it matters:

The International Personality Item Pool provides public-domain items and scales
for personality research and measurement. It is the best first candidate for a
prototype because it avoids many licensing constraints attached to commercial
inventories.

Project use:

- prototype self-report assessment
- broad OCEAN calibration
- facet-level calibration when using longer IPIP-NEO forms
- validation benchmark for passively inferred hypotheses

Cautions:

- Choose the exact IPIP scale deliberately; "IPIP" is a pool, not one test.
- Longer forms improve facet coverage but increase onboarding burden.
- Self-report results should remain editable and contextualized.

Source links:

- https://ipip.ori.org/
- https://ipip.ori.org/newPermission.htm
- https://ipip.ori.org/newCitation.htm

### Ten Item Personality Inventory

Assessment id: `tipi`

Primary constructs:

- Big Five broad traits

Use posture: `usable_now`

Why it matters:

TIPI is a very short Big Five measure that can support fast onboarding,
calibration smoke tests, and early user feedback loops.

Project use:

- fast prototype intake
- lightweight calibration when personality is not the main flow
- comparison point for longer instruments

Cautions:

- Very short scales sacrifice precision.
- Treat TIPI as a coarse starting signal, not a strong trait estimate.
- It is not suitable for facet-level generation control.

Source link:

- https://gosling.psy.utexas.edu/scales-weve-developed/ten-item-personality-measure-tipi/

### Big Five Inventory-2 Family

Assessment id: `bfi2_family`

Primary constructs:

- Big Five domains
- 15 hierarchical facets

Use posture: `license_review`

Why it matters:

BFI-2 is a strong reference model for trait-to-facet structure. Its 15-facet
hierarchy is especially useful for designing profile atom granularity even if
the product does not administer the BFI-2 directly.

Project use:

- construct crosswalk
- facet naming reference
- validation target if licensing permits

Cautions:

- Do not copy or administer items until permissions and commercial-use terms are
  verified.
- A validated self-report instrument does not prove that passive user data can
  estimate the same facets.

Source:

- Soto, C. J., and John, O. P. (2017). The Next Big Five Inventory (BFI-2):
  Developing and Assessing a Hierarchical Model With 15 Facets. Journal of
  Personality and Social Psychology, 113(1), 117-143.
  https://doi.org/10.1037/pspp0000096

### Big Five Aspects Scale

Assessment id: `big_five_aspects_scale`

Primary constructs:

- 10 Big Five aspects between broad traits and facets

Use posture: `license_review`

Why it matters:

The aspect level may be a useful middle layer for Sol because it is more precise
than broad OCEAN scores but less burdensome than full facet models.

Project use:

- profile atom hierarchy design
- intermediate generation mapping
- comparison with BFI-2 and IPIP facet structures

Cautions:

- Confirm item and scoring permissions before use.
- Aspect constructs should still be treated as inferred tendencies, not direct
  observations.

Source:

- DeYoung, C. G., Quilty, L. C., and Peterson, J. B. (2007). Between Facets and
  Domains: 10 Aspects of the Big Five. Journal of Personality and Social
  Psychology, 93(5), 880-896. https://doi.org/10.1037/0022-3514.93.5.880

### BFI-10

Assessment id: `bfi10`

Primary constructs:

- Big Five broad traits

Use posture: `license_review`

Why it matters:

BFI-10 is another very short Big Five measure. It may be useful as a comparator
to TIPI if we need a minimal onboarding assessment.

Project use:

- onboarding comparison
- survey-length tradeoff experiments

Cautions:

- Very short scales are not adequate for high-confidence trait or facet claims.
- Confirm permissions and scoring before product use.

Source:

- Rammstedt, B., and John, O. P. (2007). Measuring personality in one minute or
  less: A 10-item short version of the Big Five Inventory in English and German.
  Journal of Research in Personality, 41(1), 203-212.
  https://doi.org/10.1016/j.jrp.2006.02.001

### HEXACO-PI-R

Assessment id: `hexaco_pi_r`

Primary constructs:

- Honesty-Humility
- Emotionality
- Extraversion
- Agreeableness
- Conscientiousness
- Openness to Experience

Use posture: `license_review`

Why it matters:

HEXACO is not strictly OCEAN, but it is adjacent and useful because
Honesty-Humility may capture socially relevant variance that Big Five models do
not isolate as cleanly.

Project use:

- adjacent model comparison
- later profile model expansion
- cautionary check against overcommitting to OCEAN only

Cautions:

- Confirm research, teaching, commercial, translation, and item storage terms.
- Do not force HEXACO constructs into OCEAN labels.

Source link:

- https://hexaco.org/

### NEO PI-R / NEO-PI-3 / NEO-FFI

Assessment id: `neo_family`

Primary constructs:

- Five-Factor Model domains
- 30 facets for longer NEO instruments

Use posture: `reference_only`

Why it matters:

The NEO family is a major reference point for Big Five / Five-Factor Model
measurement and facet structure.

Project use:

- construct comparison
- historical and psychometric reference
- validation literature review

Cautions:

- Treat as proprietary/reference-only unless licensing and qualified-use
  requirements are satisfied.
- Do not reproduce items.
- Do not use in clinical, employment, or eligibility contexts.

Source:

- Costa, P. T., and McCrae, R. R. (1992). Revised NEO Personality Inventory
  manual. Psychological Assessment Resources.

## First Recommendation

Use IPIP as the first real assessment source and optionally use TIPI as a
low-friction onboarding prototype. Use BFI-2, BFAS, and NEO as structure and
validation references until permissions are resolved.
