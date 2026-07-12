# Creative Style Kit Guidance Lifecycle

## Scope

`tools/style_kit_guidance.py` is the domain boundary for concrete generation
guidance. It operates on the contract-backed local repository and deliberately
does not provide routes, UI, prompt construction, generation providers, or
pilot-run persistence.

Guidance is a user-reviewed instruction for one or more writing contexts and
task scopes. It is not a personality fact, assessment score, or silent rewrite
of source evidence.

## Lifecycle

Every new record starts `proposed` with no review history. Creation never makes
guidance generation-eligible.

Allowed transitions:

| From | To |
|---|---|
| `proposed` | `confirmed`, `edited`, `disabled` |
| `confirmed` | `edited`, `disabled` |
| `edited` | `edited`, `disabled` |
| `disabled` | none |

Confirmation cannot include content edits. A material instruction, prompt-safe
instruction, context, task-scope, or contraindication change uses the `edited`
state. Disabling is a separate operation and cannot be combined with edits.

Each successful review:

- normalizes `reviewed_at` to UTC;
- increments `guidance_version`;
- updates `updated_at`;
- appends field-level `from`/`to` history;
- preserves `original_instruction`.

## Evidence Eligibility

Guidance must reference at least one observation or eligible profile atom and
must retain source-level Style Kit consent.

An observation may support a proposal when it is active, not
rejected/invalidated, and low or medium sensitivity. Activation additionally
requires the observation to be user-confirmed.

Profile atoms use the shared policy in `tools/profile_atom_policy.py`. An atom
is eligible only when it is:

- `active_atom`;
- `contextual` or `global`;
- user `confirmed` or `edited`;
- not sensitivity `blocked`.

Suppressed, rejected, provisional, review-only, or blocked atoms cannot activate
guidance. If evidence becomes ineligible later, `eligible_guidance` excludes the
guidance immediately even before a later cleanup operation disables the stored
record.

## Assessment Boundary

Assessment-derived atoms may be cited as optional evidence only after they pass
the shared eligibility policy. The service never converts an atom claim,
domain, score, or `generation_mappings` value into an instruction.

Even a `deterministic_mapping` proposal stays `proposed` until a user explicitly
confirms or edits it. Review does not modify the referenced assessment atom,
assessment response, score, claim, or confidence.

## Prompt-Safe Representation

`instruction` and `prompt_safe_instruction` are separate required fields. An
instruction edit must supply its prompt-safe representation explicitly; the
service does not guess, sanitize, or silently repair it. Both changes appear in
review history.

Prompt construction and output safety validation remain Increment 3 work.

## Atomicity

Reviews use the repository's `mutate_record` operation. The current record,
evidence check, transition, full-bundle validation, and atomic filesystem
replacement occur under the same in-process repository lock. Failed reviews do
not change persisted bytes.

## Validation

```bash
python3 -m unittest tests.test_style_kit_guidance
./scripts/run_assessment_web_mvp_qa.sh
```

The tests cover the complete transition matrix, immutable original wording,
prompt-safe edit history, owner and timestamp boundaries, evidence changes,
context/task filters, atom exclusions, and explicit user activation.
