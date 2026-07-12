# Creative Style Kit Contracts v1

This directory contains the machine-readable record contracts selected in
`docs/adr/2026-07-12-style-kit-record-contracts.md`.

Record schemas:

- `source.schema.json`
- `observation.schema.json`
- `generation-guidance.schema.json`
- `pilot-run.schema.json`
- `evaluation-event.schema.json`

The schemas deliberately describe independent records joined by identifiers.
Assessment sessions and profile atoms may be referenced as optional evidence,
but neither owns the Creative Style Kit flow.

Validate the schemas and the cross-linked example bundle offline:

```bash
python3 tools/validate_style_kit_contracts.py
```

Install optional development/operator dependencies when needed:

```bash
python3 -m pip install -r requirements-dev.txt
```

The first product policy supports only self-authored writing, stores it locally
until explicit deletion, and does not send it to an external provider. Schema
support for a state does not by itself approve that state for product use.
