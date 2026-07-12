# Creative Style Kit Local Repository

## Scope

`tools/style_kit_store.py` is the first persistence boundary for the Creative
Style Kit record contracts. It deliberately provides storage only: no routes,
guidance transitions, generation provider, or UI behavior are part of this
increment.

## Provider And Location

The provider is a single-process, filesystem-backed JSON repository.

- Default manual path: `tmp/style-kit/style-kit-records.json`
- Override: `SOL_STYLE_KIT_DB=/absolute/path/to/style-kit-records.json`
- Automated tests: isolated system temporary directories

The default path is ignored by Git. Reading an absent repository returns an
empty versioned bundle without creating a file. The first successful mutation
creates the parent directory and writes the file with user-only permissions.

No credentials, network service, container, port, or external provider is
required.

## Operations

`JsonStyleKitRepository` implements the `StyleKitRepository` protocol:

- load or replace the complete versioned bundle;
- list a collection;
- get a record by id;
- create a record;
- replace a record without changing its id.

Collections are limited to:

- `sources`;
- `observations`;
- `generation_guidance`;
- `pilot_runs`;
- `evaluation_events`.

Every successful mutation validates the complete proposed bundle against the
five JSON Schemas and the cross-record consent/provenance rules before writing.
Callers receive deep copies so in-memory edits cannot bypass the repository.

## Atomicity And Concurrency

Mutations are serialized by one in-process reentrant lock. Writes use a
same-directory temporary file, flush and `fsync`, then atomically replace the
repository file. Failed validation occurs before replacement and must leave the
existing bytes unchanged.

This is not a multi-process or multi-user database. Those requirements remain
deferred until the product wedge demonstrates value.

## Validation

```bash
python3 -m unittest tests.test_style_kit_store
python3 tools/validate_style_kit_contracts.py
./scripts/run_assessment_web_mvp_qa.sh
```

The tests prove read-after-write for all record types, invalid-write atomicity,
copy isolation, and concurrent in-process creation. They do not write to the
default repository or tracked JSONDB files.

## Manual Cleanup

No process remains running after repository operations. If manual experiments
create the default local file, remove only that file with:

```bash
rm -f tmp/style-kit/style-kit-records.json
```

Do not remove `jsondb/`, assessment sessions, or the complete `tmp/` tree as
part of this cleanup.
