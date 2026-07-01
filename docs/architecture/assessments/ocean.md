# OCEAN Assessment Architecture

## Purpose

The OCEAN assessment area stores instruments that can support self-report
calibration, scoring, result presentation, and profile atom generation.

The assessment area is separate from the research KB because it contains
administrable instrument data rather than only interpretive notes.

## Directory Layout

```text
assessments/
  README.md
  ocean/
    README.md
    manifest.json
    instruments/
      *.json
    reference_only/
      ocean_reference_inventory.json
```

## Storage Rule

Store full item text only when the instrument is clearly public-domain or
explicitly permissive. Otherwise store metadata only and keep the instrument in
the reference-only queue.

## MVP Use

The MVP web app should initially load from `assessments/ocean/manifest.json`,
select one instrument from `assessments/ocean/instruments/`, administer items
with the instrument's response scale, score according to the stored keying
metadata, and write assessment-derived profile atom candidates.

Recommended first app candidates:

- `tipi.json` for very fast flow testing.
- `mini_ipip.json` for a short but slightly richer OCEAN path.
- `ipip_neo_60_maples_keller_2019.json` for a compact NEO-domain style path.

Longer IPIP forms are better suited for validation, item analysis, and
construct mapping than first-run user onboarding.

## Result Safety

Results should be presented as self-report tendencies with uncertainty, not as
diagnoses or fixed identity claims. The UI should give users controls to edit,
reject, hide, export, and delete assessment-derived profile atoms.
