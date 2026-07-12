# 2026-07-12: Assessment Session Integrity And Data Control

## Problem Statement

The local assessment MVP used a threaded HTTP server over an unlocked JSON
read-modify-write store. It also accepted response values without validating
them against the instrument, stored no durable consent receipt or immutable
instrument fingerprint, allowed reviewed atoms to be overwritten by rescoring,
and exposed only whole-session deletion.

These gaps conflict with the repository's research-first, user-correctable, and
data-control posture even though the app remains a local MVP.

## Options Evaluated

### Option A: Leave Integrity To The Future Application Database

| Pros | Cons |
|------|------|
| No additional JSONDB complexity | Current MVP can lose or accept invalid evidence |
| Faster feature work | Consent/version claims remain unsupported |

### Option B: Harden The Single-Process JSONDB Boundary

| Pros | Cons |
|------|------|
| Fixes current correctness risks with small scope | Still not multi-process or production storage |
| Shared validation covers CLI and web callers | Requires explicit migration/backward compatibility |
| Preserves local-first development | Completed sessions become intentionally less mutable |

### Option C: Replace JSONDB Immediately

| Pros | Cons |
|------|------|
| Stronger transactions and migrations | Premature platform work before the wedge is validated |
| Better multi-user path | Much larger change and operational surface |

## Decision

Choose Option B for the current MVP.

The session store is the trust boundary for response validation, consent and
instrument provenance, lifecycle invariants, atomic mutation, rescoring safety,
and selective deletion. Completed-session responses are immutable; a changed
assessment should create a new session. Rescoring a reviewed session is blocked
rather than attempting a silent merge of old user corrections with new derived
claims.

## Implementation Details

- Validate response item IDs and values against the stored instrument.
- Restore item-count confidence fallback bands and test their boundaries.
- Normalize event timestamps to timezone-aware UTC ISO strings.
- Persist consent version/timestamp/scope, instrument schema version, scoring
  method, and SHA-256 fingerprint on new sessions.
- Refuse scoring or response mutation if the stored instrument fingerprint has
  changed.
- Serialize in-process mutations with a reentrant lock and write JSON through
  an atomic same-directory temporary-file replacement.
- Enforce compatible state/scope/feedback combinations for atom review.
- Prevent reviewed atoms from being overwritten by rescoring.
- Support separate deletion of raw responses, derived profile atoms, or the
  entire session; clean feedback references when atoms or sessions are deleted.
- Keep existing tracked sessions readable. New integrity fields are required
  for new sessions and are not fabricated for historical records.

This remains a single-process local store. A multi-user or multi-process app
still requires a transactional application database and migration framework.

