#!/usr/bin/env bash
set -euo pipefail

python3 -m py_compile \
  tools/assessment_session_store.py \
  tools/assessment_web_mvp.py \
  tools/assessment_to_profile_atoms.py \
  tools/generation_pilot.py \
  tools/validate_sol_ocean_candidate.py

python3 tools/validate_sol_ocean_candidate.py >/dev/null

python3 -m json.tool jsondb/assessment_sessions.json >/dev/null

if command -v node >/dev/null 2>&1; then
  node --check app/assessment-mvp/app.js
fi

python3 -m unittest discover -s tests

if git diff --quiet -- jsondb/assessment_sessions.json; then
  echo "assessment_sessions.json unchanged"
else
  echo "assessment_sessions.json changed during QA" >&2
  exit 1
fi
