# 2026-07-08: Profile Atom Lifecycle and Activation Contract

## Problem Statement

The repository now has enough research support to distinguish between:

- raw observations
- candidate interpretations
- user-confirmed or high-confidence profile atoms
- atoms that are allowed to steer generation

Without a formal contract, implementation work could collapse these layers into
one flat profile object. That would make the system harder to audit, easier to
overclaim, and more likely to let weak signals directly control output.

Constraints:

- The product must remain non-diagnostic and user-correctable.
- The first MVP is assessment-first, but the schema must also support future
  text, preference, and feedback evidence.
- The contract must preserve context, uncertainty, provenance, and user agency.
- The repo should support both background retrieval and operational product
  implementation.

## Options Evaluated

### Option A: Single Flat Atom Type

Store all profile items in one shape with no explicit lifecycle or activation
distinction.

| Pros | Cons |
|------|------|
| Simple to implement at first | Weak signals can look equivalent to confirmed ones |
| Fewer fields and transitions | Harder to audit promotion logic |
| Easy to serialize | Encourages overuse of inferred traits as generation controls |

### Option B: Lifecycle-Based Atom Contract

Use one base schema with explicit lifecycle states and activation scope.

| Pros | Cons |
|------|------|
| Preserves separation between observation, candidate, and active atom | More schema fields and transition rules |
| Supports thresholding and user confirmation | Requires explicit promotion logic |
| Better fit for provenance, recency, and uncertainty | Slightly more work for MVP storage and UI |
| Matches current research model and safety posture | Needs discipline to keep transitions consistent |

### Option C: Separate Schemas Per Pipeline Stage

Use different object types for observations, candidates, active atoms, and
generation controls.

| Pros | Cons |
|------|------|
| Strongest type separation | More complex storage and migration path |
| Clear boundaries between stages | Higher implementation overhead for early MVP |
| Easier long-term specialization | More difficult to inspect as one coherent atom history |

## Decision

Choose Option B: lifecycle-based atom contract.

This keeps one coherent profile-atom object while making the important state
transitions explicit. It fits the current research direction:

- candidate-vs-active distinction from the updated ontology
- thresholding and reportability ideas from the Baars/Dehaene source cluster
- user-correctable profile design already established in project memory

Option A is too loose for a system that wants to be evidence-backed and
inspectable. Option C may become appropriate later if the backend grows into a
larger multi-service platform, but it is too heavy for the current stage.

## Implementation Details

Added:

- `kb/model/profile_atom_schema_v0.md`
- this ADR

The schema contract defines:

- required base fields
- lifecycle states
- activation scopes
- evidence expectations
- promotion and suppression rules

Near-term implementation implications:

- assessment outputs should create `provisional_atom` records, not immediately
  `active_atom` records
- direct user corrections and confirmations should update lifecycle state and
  activation scope
- generation code should consume only atoms that are eligible for activation
  under the contract

Follow-up work:

- add a machine-readable JSON Schema once the MVP storage contract settles
- align assessment scoring output with `profile_atom_schema_v0.md`
- add a profile-atom persistence model for sessions and user feedback
