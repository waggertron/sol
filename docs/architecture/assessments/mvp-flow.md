# Assessment MVP Flow

This document defines the first executable end-to-end assessment workflow in
the repository.

## Goal

Provide one local command that:

1. creates an assessment session
2. stores raw responses
3. computes scores
4. derives provisional profile atoms
5. writes export artifacts for later UI or generation work

## Tool

- `tools/run_assessment_mvp.py`

## Inputs

- stored instrument JSON from `assessments/ocean/instruments/`
- response JSON keyed by item id or source order
- session id
- timestamps

## Outputs

Artifacts are written to:

- `artifacts/assessment_runs/<session_id>/session.json`
- `artifacts/assessment_runs/<session_id>/summary.json`

`session.json` contains:

- session metadata
- raw responses
- derived scores
- derived `provisional_atom` profile candidates

`summary.json` contains:

- concise session metadata
- compact profile atom summaries for early UI or inspection

## Example

```bash
python3 tools/run_assessment_mvp.py \
  --session-id session_tipi_example \
  --instrument assessments/ocean/instruments/tipi.json \
  --responses assessments/ocean/examples/tipi_sample_responses.json \
  --started-at 2026-07-08T21:00:00Z \
  --completed-at 2026-07-08T21:05:00Z
```

Mini-IPIP smoke example:

```bash
python3 tools/run_assessment_mvp.py \
  --session-id session_mini_ipip_example \
  --instrument assessments/ocean/instruments/mini_ipip.json \
  --responses assessments/ocean/examples/mini_ipip_sample_responses.json \
  --started-at 2026-07-08T21:15:00Z \
  --completed-at 2026-07-08T21:20:00Z
```

## Current Role

This is the first practical app boundary in the repo.

Future UI or API layers should treat this flow as the reference behavior until
they replace it with a richer application-backed implementation.
