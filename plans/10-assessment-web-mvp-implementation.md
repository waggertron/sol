# Assessment Web MVP Implementation Plan

## Purpose

Record the next execution steps after the assessment-first CLI MVP so the repo
keeps a visible implementation history.

## Current Baseline

As of 2026-07-08, the repository already has:

- stored OCEAN instruments under `assessments/ocean/`
- a scoring and profile-atom generator in `tools/assessment_to_profile_atoms.py`
- JSONDB-backed session persistence in `tools/assessment_session_store.py`
- an executable CLI flow in `tools/run_assessment_mvp.py`

What it does not yet have is a user-facing assessment administration surface.

## Next Execution Steps

### Step 1: Web Surface

Build a thin local web app that can:

- load the assessment manifest
- select one stored instrument
- present a consent gate
- render assessment items from repo JSON
- autosave responses into the existing session store
- score the session on completion
- present stored scores and derived profile atoms

### Step 2: Review Controls

Expose the current profile-atom lifecycle directly in the UI:

- confirm atom
- reject atom
- mark edited atom
- show current atom state and activation scope

Current implementation note: the first browser workbench now supports
cross-session atom review for confirm, reject, and review-only states.

### Step 3: Storage and Contract Hardening

Harden the assessment-session contract around:

- partial response saves
- session resume by id
- clear distinction between raw responses and derived atoms
- explicit timestamps for start, save, score, and review actions

Current implementation note: the local web API now exposes session listing,
session JSON export, and whole-session deletion through the shared JSONDB
session store.

### Step 4: Documentation

Update repo docs so the current runnable MVP is clear:

- where the web app lives
- how to start it
- which instruments are supported first
- what remains local-only and experimental

### Step 5: Follow-On Implementation Targets

After the first web MVP is stable, the next likely slices are:

1. profile workbench view for multi-session review
2. export and delete flows
3. richer score explanation and uncertainty text
4. support for additional permissive instruments
5. migration from JSONDB files to an application data store

## Acceptance Criteria For This Slice

- A user can start a session from a browser.
- A user can complete at least one stored instrument end to end.
- The UI writes data into `jsondb/assessment_sessions.json` through the current
  MVP storage layer.
- The UI can display derived scores and provisional profile atoms.
- The UI can update atom review state without direct CLI usage.
