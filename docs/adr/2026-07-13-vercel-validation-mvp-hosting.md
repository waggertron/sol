# 2026-07-13: Vercel Hosting For Validation MVP

## Problem Statement

The participant-link validation MVP needs a shareable URL for real users without
requiring accounts. The current app is a local Python `ThreadingHTTPServer`
backed by local JSON files. That is suitable for local validation, but it is not
a hosted multi-user pilot boundary: serverless deployments are stateless across
invocations, local file writes are not a durable persistence model, and model
provider credentials must not be exposed to the browser.

The hosting choice must preserve the MVP's safety posture:

- no-auth participant links;
- opaque participant IDs for resume/export/delete;
- no high-stakes scenarios;
- explicit external-provider disclosure;
- proof that the organic response is excluded from predicted-response requests;
- no silent mutation of assessment evidence, atom claims, confidence, or model
  weights.

## Options Evaluated

### Option A: Keep The Pilot Local Only

Run the participant-link MVP from a local machine and manually share tunnels or
screens.

| Pros | Cons |
|------|------|
| Minimal engineering change | Not reliable for real participant links |
| Keeps JSONDB unchanged | Weak participant resume/export/delete story |
| No cloud data handling yet | Hard to run asynchronous user validation |

### Option B: Vercel Frontend And API With Hosted Postgres

Deploy the participant UI and API on Vercel. Keep the API stateless and persist
pilot records in a hosted Postgres database provisioned through the Vercel
Marketplace, such as Neon or another approved provider.

| Pros | Cons |
|------|------|
| Fastest shareable public pilot URL | Requires replacing JSONDB for hosted MVP data |
| Vercel supports server-side functions and Python runtime | Python runtime is currently documented as beta |
| Built-in previews, environment variables, logs, and rollbacks | Need explicit log redaction and retention discipline |
| Easy to keep participant flow no-auth | Production URL is public unless protected by plan/add-on controls |

### Option C: Traditional App Host

Deploy a persistent Python web app on Render, Fly.io, Railway, or a small VPS.

| Pros | Cons |
|------|------|
| Closer to current local server model | More operations work before validation |
| Easier local-file mental model | Still needs durable database for pilot integrity |
| Full process control | Slower to get a polished shareable link |

## Decision

Choose Option B for the validation MVP.

Vercel is appropriate for the first real-user participant pilot if we treat it
as a stateless web/API host and move participant data into a hosted database.
Do not deploy the current JSONDB-backed server unchanged. Keep the broader
platform decision open until the validation MVP produces evidence.

Use Vercel for:

- the public participant route;
- same-origin API routes;
- server-side model-provider calls after explicit pilot-provider approval;
- deployment previews and production rollback.

Use hosted Postgres for:

- pilot links;
- participant records;
- scenarios;
- organic responses;
- assessment sessions or hosted assessment-session mirrors;
- predicted-response run records;
- ranking records;
- alignment feedback;
- export/delete tombstones.

## Implementation Details

### Current Official Constraints

- Vercel Functions run server-side code without managing servers and support
  multiple runtimes, including Python.
- Vercel's Python runtime is documented as beta and supports ASGI/WSGI apps,
  Python entrypoints, and `/api` Python functions.
- Vercel Functions with Fluid Compute have documented duration limits that are
  sufficient for one short assessment scoring/generation request.
- Function request/response payloads are capped at 4.5 MB, so the MVP's short
  scenario and response limits stay well below the platform limit.
- Vercel Postgres is no longer available for new projects; use an external
  Postgres provider through the Vercel Marketplace.
- Deployment Protection can protect preview deployments, but a no-auth
  participant production flow should rely on an unguessable pilot URL and
  application-level participant ID rather than Vercel Authentication.

References:

- <https://vercel.com/docs/functions>
- <https://vercel.com/docs/functions/runtimes/python>
- <https://vercel.com/docs/functions/limitations>
- <https://vercel.com/docs/functions/configuring-functions/duration>
- <https://vercel.com/docs/postgres>
- <https://vercel.com/docs/deployment-protection>

### Proposed Shape

- `app/assessment-mvp/` remains the local prototype until the hosted pilot shell
  is introduced.
- Add a deployable participant pilot surface separately, either:
  - static HTML/JS served by Vercel plus `/api` Python functions; or
  - a small Next.js shell that calls Python or TypeScript API routes.
- Prefer the smallest migration first: static participant UI plus Python API
  functions that reuse existing assessment/scoring modules.
- Add a hosted repository abstraction before route work. It should share
  validation behavior with local stores but persist to Postgres.
- Keep all provider keys in Vercel environment variables. Never expose model
  credentials to client JavaScript.

### Minimal Hosted Tables

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

All tables need `created_at`, `updated_at`, `participant_id` where applicable,
schema/version fields, and deletion/export state.

### Access Boundary

- Participant route: public but requires an unguessable pilot slug.
- Participant resume/export/delete: requires the opaque participant ID.
- Admin/report routes: not part of the no-auth flow; protect with deployment
  protection, a separate admin secret, or keep local-only for the first pilot.
- Logs: do not log raw responses, raw assessment answers, provider prompts, or
  predicted outputs.

### Rollout

1. Add hosted data-contract plan and SQL schema draft.
2. Build local Postgres-compatible repository tests against temporary storage
   or a local mock.
3. Add Vercel API route smoke tests without external model calls.
4. Deploy preview with mock provider only.
5. Verify participant export/delete and organic-response exclusion.
6. Enable a narrow production pilot link.
7. Approve real provider use separately, with explicit participant disclosure.
