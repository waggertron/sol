# OCEAN Assessments

This area contains acquired Big Five / OCEAN and OCEAN-adjacent assessment
materials for prototype administration and scoring.

## Imported Instruments

The current import is summarized in:

- `manifest.json`

Stored instruments live in:

- `instruments/*.json`

Current import scope:

- IPIP Goldberg Big-Five Factor Markers
- Mini-IPIP
- Mini-IPIP6
- IPIP Big Five Aspects Scales
- IPIP AB5C 45 Facets
- IPIP NEO domain representation
- IPIP NEO facet representation
- IPIP-NEO-120 Johnson 2014
- IPIP-NEO-120 Maples et al. 2014
- IPIP-NEO-60 Maples-Keller et al. 2019
- Ten Item Personality Inventory

## Permission Posture

The IPIP instruments are imported because the official IPIP site states that its
items and scales are public domain and usable for any purpose.

TIPI is imported because the official TIPI page explicitly permits use for any
purpose.

Other OCEAN instruments are tracked as reference-only or license-review
candidates until item and scoring permissions are confirmed.

## Implementation Notes

IPIP scoring uses a 1-5 accuracy scale. Positive-keyed items score 1 through 5
from "Very Inaccurate" to "Very Accurate"; negative-keyed items are reverse
scored before summing.

TIPI scoring uses a 1-7 agreement scale and averages one direct item with one
reverse-scored paired item for each domain.

Assessment results should be treated as self-report evidence, not as fixed
identity labels. Any score-derived profile atom should remain user-visible,
editable, and non-diagnostic.

## Known Import Caveats

- `ipip_neo_120_maples_2014.json` currently contains 118 parsed items from the
  official HTML source. Two facets expose three keyed rows in that HTML source,
  so the import preserves the source-derived count instead of inventing missing
  rows.
- Some IPIP items include sensitive or product-risky content, such as political
  orientation or self-evaluation language. These items are flagged with
  `review_flags` where simple keyword detection catches them.
- `mini_ipip6.json` is OCEAN-adjacent because it includes Honesty-Humility in
  addition to the five broad factors.
