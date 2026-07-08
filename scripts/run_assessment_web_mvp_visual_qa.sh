#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_ROOT="${1:-tmp/assessment-web-mvp-visual}"
case "${ARTIFACT_ROOT}" in
  tmp/assessment-web-mvp-visual*) ;;
  *)
    echo "Artifact path must stay under tmp/assessment-web-mvp-visual*" >&2
    exit 1
    ;;
esac

rm -rf "${ARTIFACT_ROOT}"
mkdir -p "${ARTIFACT_ROOT}"

export SOL_ASSESSMENT_SESSIONS_DB="${ARTIFACT_ROOT}/assessment_sessions.json"

python3 tools/run_assessment_mvp.py \
  --session-id visual_tipi_session \
  --instrument assessments/ocean/instruments/tipi.json \
  --responses assessments/ocean/examples/tipi_sample_responses.json \
  --started-at 2026-07-08T22:00:00Z \
  --completed-at 2026-07-08T22:05:00Z \
  --artifact-dir "${ARTIFACT_ROOT}/artifacts" >/dev/null

python3 tools/run_assessment_mvp.py \
  --session-id visual_mini_ipip_session \
  --instrument assessments/ocean/instruments/mini_ipip.json \
  --responses assessments/ocean/examples/mini_ipip_sample_responses.json \
  --started-at 2026-07-08T22:10:00Z \
  --completed-at 2026-07-08T22:15:00Z \
  --artifact-dir "${ARTIFACT_ROOT}/artifacts" >/dev/null

PORT="${SOL_ASSESSMENT_VISUAL_QA_PORT:-8768}"
BASE_URL="http://127.0.0.1:${PORT}"
python3 tools/assessment_web_mvp.py --port "${PORT}" >"${ARTIFACT_ROOT}/server.log" 2>&1 &
SERVER_PID=$!

cleanup() {
  if kill -0 "${SERVER_PID}" >/dev/null 2>&1; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

for _ in $(seq 1 50); do
  if curl -fsS "${BASE_URL}/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done

curl -fsS "${BASE_URL}/api/health" >/dev/null

run_playwright() {
  if command -v playwright >/dev/null 2>&1; then
    playwright "$@"
  else
    npx playwright "$@"
  fi
}

run_playwright screenshot \
  --viewport-size "1440,1000" \
  --wait-for-selector "#instrument-list .instrument-button" \
  --timeout 10000 \
  "${BASE_URL}/#administer" \
  "${ARTIFACT_ROOT}/admin-desktop.png"

run_playwright screenshot \
  --viewport-size "390,844" \
  --wait-for-selector "#instrument-list .instrument-button" \
  --timeout 10000 \
  "${BASE_URL}/#administer" \
  "${ARTIFACT_ROOT}/admin-mobile.png"

run_playwright screenshot \
  --viewport-size "1440,1000" \
  --wait-for-selector "#workbench-atoms .atom-card" \
  --timeout 10000 \
  "${BASE_URL}/#workbench" \
  "${ARTIFACT_ROOT}/workbench-desktop.png"

run_playwright screenshot \
  --viewport-size "390,844" \
  --full-page \
  --wait-for-selector "#workbench-atoms .atom-card" \
  --timeout 10000 \
  "${BASE_URL}/#workbench" \
  "${ARTIFACT_ROOT}/workbench-mobile.png"

if git diff --quiet -- jsondb/assessment_sessions.json; then
  echo "assessment_sessions.json unchanged"
else
  echo "assessment_sessions.json changed during visual QA" >&2
  exit 1
fi

echo "visual QA screenshots written to ${ARTIFACT_ROOT}"
