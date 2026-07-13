# Validation MVP Hosting Plan

## Purpose

Host the participant-link validation MVP behind a shareable URL so 5-8 real
participants can complete the flow asynchronously:

```text
pilot link -> participant ID -> scenario -> organic response -> assessment
  -> predicted response -> ranking -> alignment feedback -> export/delete
```

The selected hosting path is Vercel plus hosted Postgres, documented in
`docs/adr/2026-07-13-vercel-validation-mvp-hosting.md`.

## Resume Note

Resume here with H0 and V0 before writing hosted route code:

1. Confirm the Vercel project/domain, hosted Postgres provider, API stack
   choice, environment variable names, and region.
2. Draft participant consent, provider disclosure, retention/export/delete copy,
   and the first safe scenario module set.
3. Then implement the hosted persistence boundary and route skeleton in mock or
   dry-run mode only.

Do not deploy the JSONDB-backed local server unchanged. Do not enable real model
provider calls until provider disclosure, request inspection, output validation,
export/delete, and the organic-response exclusion test are in place.

## Hosting Decision

Use Vercel for the validation MVP, but do not deploy the current local JSONDB
server unchanged.

Vercel is a good fit for:

- fast public participant links;
- preview deployments;
- same-origin API routes;
- environment-managed provider keys;
- rollback after a bad pilot deployment.

Vercel is not the persistence layer. Hosted pilot data must live in Postgres or
another reviewed external datastore.

## Target Architecture

```text
Participant browser
  -> Vercel static/edge delivery
  -> same-origin API function
  -> hosted Postgres
  -> optional model provider after explicit gate
```

Initial implementation should keep the UI small:

- `/p/{pilot_slug}` starts or resumes the participant flow.
- `/api/pilot/*` owns participant, scenario, response, assessment, prediction,
  feedback, export, and delete operations.
- `/api/admin/*` is deferred or protected separately; it is not part of the
  no-auth participant flow.

## Required Hosting Contracts

### Participant Link

- Pilot links are unguessable.
- The production participant route is public.
- The route should reveal no participant data without the opaque
  `participant_id`.
- Preview deployments may use Vercel Deployment Protection; production
  participant links cannot require Vercel login if the pilot is no-auth.

### Participant ID

- Generate a high-entropy opaque ID.
- Tell the participant to write it down.
- Use it for resume, export, and delete.
- Do not use sequential IDs or email addresses.

### Persistence

Replace JSONDB for hosted pilot records with Postgres tables:

- `pilot_links`
- `participants`
- `participant_events`
- `scenarios`
- `organic_responses`
- `assessment_sessions`
- `assessment_scores`
- `assessment_atoms`
- `prediction_runs`
- `response_rankings`
- `alignment_feedback`
- `deletion_requests`

Keep raw response text, assessment answers, prompts, provider responses, and
feedback out of application logs.

### Model Provider

Default deployment mode remains `mock` or `dry-run`.

Real model use requires:

- explicit provider disclosure in the participant flow;
- environment-stored API key;
- request inspection proving `organic_response_excluded: true`;
- persisted prompt/context/request hashes;
- output validation and redaction on failure;
- a kill switch to disable provider calls without redeploying.

## Implementation Increments

### H0: Hosting Preflight

- [ ] Choose Vercel project name and production domain/subdomain.
- [ ] Choose hosted Postgres provider from the Vercel Marketplace.
- [ ] Decide whether the first hosted API is Python `/api` functions or a small
  Next.js API shell.
- [ ] Draft environment variable names without committing secrets.
- [ ] Decide the Vercel region to match the database region.

Acceptance:

- no participant data can be written to repo files in the hosted path;
- provider keys are server-only environment variables.

### H1: Hosted Data Contract

- [ ] Write SQL schema or migration draft for pilot records.
- [ ] Add repository interface for hosted participant-pilot persistence.
- [ ] Preserve local mock/temp storage for tests.
- [ ] Add export/delete tombstone behavior.

Acceptance:

- local tests prove create/read/export/delete for one participant record graph;
- schema records consent, scenario version, assessment fingerprint, prediction
  request hash, ranking method, and feedback version.

### H2: Vercel Route Skeleton

- [ ] Add deployable participant UI route.
- [ ] Add health check and pilot-start API route.
- [ ] Add scenario/organic-response save API route.
- [ ] Add assessment bridge API route.
- [ ] Add export/delete API routes.

Acceptance:

- preview deployment can complete link -> ID -> scenario -> organic response in
  mock mode;
- no route logs raw participant text.

### H3: Prediction And Ranking

- [ ] Add predicted-response API route with mock provider first.
- [ ] Add request-inspection test for organic-response exclusion.
- [ ] Add ranking route or service for organic and predicted responses.
- [ ] Persist run/ranking hashes and versions.

Acceptance:

- predicted response can be generated without organic-response leakage;
- both responses receive prompt-answering rankings.

### H4: Feedback And Pilot Launch

- [ ] Add alignment feedback UI and API route.
- [ ] Add local/admin report export for pilot results.
- [ ] Configure production pilot link.
- [ ] Run final export/delete smoke test.
- [ ] Gate real provider use separately.

Acceptance:

- 5-8 participants can complete the hosted pilot;
- each participant can export/delete their records by ID;
- pilot report separates prompt-answering quality from voice alignment.

## Vercel Notes

- Keep payloads well below Vercel Function body limits by enforcing the scenario
  and response length limits from `plans/16`.
- Configure function max duration explicitly for any route that calls an
  external model.
- Prefer same-origin relative fetches from the browser.
- Use preview deployments for operator review and a single production route for
  participant links.
- Treat Vercel logs as operational metadata only; never as study storage.

## Deferred

- production account authentication;
- multi-tenant admin console;
- HIPAA/clinical workflows;
- broad profile dashboards;
- visual generation;
- long-running batch analysis;
- automatic model training from feedback.
