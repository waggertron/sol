const state = {
  manifest: null,
  selectedInstrument: null,
  session: null,
  sessions: [],
  profileAtoms: [],
  autosaveTimeout: null,
  currentView: "administer",
};

const elements = {
  navAdminister: document.querySelector("#nav-administer"),
  navWorkbench: document.querySelector("#nav-workbench"),
  adminView: document.querySelector("#admin-view"),
  workbenchView: document.querySelector("#workbench-view"),
  instrumentList: document.querySelector("#instrument-list"),
  selectedInstrumentName: document.querySelector("#selected-instrument-name"),
  sessionId: document.querySelector("#session-id"),
  sessionStatus: document.querySelector("#session-status"),
  exportCurrentSession: document.querySelector("#export-current-session"),
  deleteCurrentSession: document.querySelector("#delete-current-session"),
  consentCheckbox: document.querySelector("#consent-checkbox"),
  startSession: document.querySelector("#start-session"),
  scoreSession: document.querySelector("#score-session"),
  questionnaire: document.querySelector("#questionnaire"),
  responseScale: document.querySelector("#response-scale"),
  scoreResults: document.querySelector("#score-results"),
  atomResults: document.querySelector("#atom-results"),
  autosaveStatus: document.querySelector("#autosave-status"),
  reloadManifest: document.querySelector("#reload-manifest"),
  resumeSessionId: document.querySelector("#resume-session-id"),
  resumeSession: document.querySelector("#resume-session"),
  refreshWorkbench: document.querySelector("#refresh-workbench"),
  workbenchSummary: document.querySelector("#workbench-summary"),
  sessionList: document.querySelector("#session-list"),
  workbenchAtoms: document.querySelector("#workbench-atoms"),
  atomFilter: document.querySelector("#atom-filter"),
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `Request failed: ${response.status}`);
  }
  return payload;
}

function apiSessionPath(sessionId, suffix = "") {
  return `/api/sessions/${encodeURIComponent(sessionId)}${suffix}`;
}

function setAutosaveStatus(text, tone = "") {
  elements.autosaveStatus.textContent = text;
  elements.autosaveStatus.className = `status-pill${tone ? ` ${tone}` : ""}`;
}

function flattenItems(instrument) {
  if (Array.isArray(instrument.items) && instrument.items.length > 0) {
    return instrument.items;
  }
  return instrument.scales.flatMap((scale) =>
    (scale.items || []).map((item) => ({
      ...item,
      domain: scale.domain,
    })),
  );
}

function switchView(view) {
  state.currentView = view;
  elements.adminView.hidden = view !== "administer";
  elements.workbenchView.hidden = view !== "workbench";
  elements.navAdminister.classList.toggle("active", view === "administer");
  elements.navWorkbench.classList.toggle("active", view === "workbench");
  if (view === "workbench") {
    loadWorkbench().catch((error) => setAutosaveStatus(error.message, "warn"));
  }
}

function renderManifest() {
  const instruments = state.manifest?.instruments || [];
  elements.instrumentList.innerHTML = "";
  for (const instrument of instruments) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "instrument-button";
    if (state.selectedInstrument?.id === instrument.id) {
      button.classList.add("active");
    }
    button.innerHTML = `
      <strong>${instrument.name}</strong>
      <div class="instrument-meta">${instrument.item_count} items | ${instrument.scale_count} scales</div>
      <div class="instrument-meta">${instrument.license_status || "license unknown"}</div>
    `;
    button.addEventListener("click", () => {
      switchView("administer");
      loadInstrument(instrument.id).catch((error) => setAutosaveStatus(error.message, "warn"));
    });
    elements.instrumentList.appendChild(button);
  }
}

function renderResponseScale(instrument) {
  elements.responseScale.innerHTML = "";
  for (const entry of instrument.response_scale.values) {
    const token = document.createElement("div");
    token.className = "scale-token";
    token.textContent = `${entry.value} | ${entry.label}`;
    elements.responseScale.appendChild(token);
  }
}

function renderQuestionnaire() {
  const instrument = state.selectedInstrument;
  elements.questionnaire.innerHTML = "";
  if (!instrument) {
    elements.questionnaire.innerHTML = `<div class="empty-state">Select an instrument to render the questionnaire.</div>`;
    return;
  }

  const items = flattenItems(instrument);
  for (const item of items) {
    const card = document.createElement("section");
    card.className = "question-card";
    const selectedValue = state.session?.responses?.[item.id];
    const choices = instrument.response_scale.values
      .map((entry) => {
        const checked = Number(selectedValue) === Number(entry.value) ? "checked" : "";
        return `
          <label>
            <input type="radio" name="${item.id}" value="${entry.value}" ${checked}>
            <span>${entry.value}</span>
            <span class="response-label">${entry.label}</span>
          </label>
        `;
      })
      .join("");
    card.innerHTML = `
      <strong>${item.source_order || "?"}. ${item.text}</strong>
      <div class="question-meta">${(item.domain || "unknown").replaceAll("_", " ")}</div>
      <div class="choice-row">${choices}</div>
    `;
    elements.questionnaire.appendChild(card);
  }

  elements.questionnaire.querySelectorAll("input[type='radio']").forEach((input) => {
    input.addEventListener("change", onResponseChanged);
  });
}

function renderScores() {
  const scores = state.session?.scores || [];
  if (!scores.length) {
    elements.scoreResults.innerHTML = `<div class="empty-state">No scored results yet.</div>`;
    return;
  }

  elements.scoreResults.innerHTML = "";
  for (const score of scores) {
    const card = document.createElement("section");
    card.className = "score-card";
    const normalized = Math.round((score.normalized_score || 0) * 100);
    card.innerHTML = `
      <strong>${score.label}</strong>
      <div class="score-meta">
        Raw ${Number(score.raw_score).toFixed(2)} on [${score.score_min}, ${score.score_max}] | normalized ${normalized}%
      </div>
      <div class="score-bar"><div class="score-fill" style="width:${normalized}%"></div></div>
    `;
    elements.scoreResults.appendChild(card);
  }
}

function atomActionButton(label, action) {
  return `<button type="button" data-action="${action}">${label}</button>`;
}

function atomActionMapping(action) {
  return {
    confirmed: {
      user_feedback: "confirmed",
      state: "active_atom",
      activation_scope: "contextual",
    },
    rejected: {
      user_feedback: "rejected",
      state: "suppressed_atom",
      activation_scope: "review_only",
    },
    review: {
      user_feedback: "unconfirmed",
      state: "provisional_atom",
      activation_scope: "review_only",
    },
  }[action];
}

function renderAtoms() {
  const atoms = state.session?.profile_atoms || [];
  if (!atoms.length) {
    elements.atomResults.innerHTML = `<div class="empty-state">No derived atoms yet.</div>`;
    return;
  }
  elements.atomResults.innerHTML = "";
  for (const atom of atoms) {
    const card = document.createElement("section");
    card.className = "atom-card";
    card.innerHTML = `
      <strong>${atom.label}</strong>
      <div class="atom-meta">${atom.state} | ${atom.activation_scope} | feedback: ${atom.user_feedback}</div>
      <p>${atom.claim}</p>
      <div class="atom-meta">confidence ${atom.confidence} | sensitivity ${atom.sensitivity_level}</div>
      <div class="atom-actions">
        ${atomActionButton("Confirm", "confirmed")}
        ${atomActionButton("Reject", "rejected")}
        ${atomActionButton("Keep review-only", "review")}
      </div>
    `;
    card.querySelectorAll("button[data-action]").forEach((button) => {
      button.addEventListener("click", async () => {
        await applyAtomReview(state.session.session_id, atom.id, button.dataset.action);
      });
    });
    elements.atomResults.appendChild(card);
  }
}

function renderSessionMeta() {
  const hasSession = Boolean(state.session);
  elements.sessionId.textContent = state.session?.session_id || "Not started";
  elements.sessionStatus.textContent = state.session?.status || "idle";
  elements.scoreSession.disabled = !state.session || Object.keys(state.session.responses || {}).length === 0;
  elements.exportCurrentSession.disabled = !hasSession;
  elements.deleteCurrentSession.disabled = !hasSession;
}

function renderWorkbenchSummary() {
  const activeCount = state.profileAtoms.filter((atom) => atom.state === "active_atom").length;
  const provisionalCount = state.profileAtoms.filter((atom) => atom.state === "provisional_atom").length;
  const rejectedCount = state.profileAtoms.filter((atom) => atom.user_feedback === "rejected").length;
  elements.workbenchSummary.innerHTML = `
    <div class="summary-card"><strong>${state.sessions.length}</strong><span>sessions</span></div>
    <div class="summary-card"><strong>${state.profileAtoms.length}</strong><span>atoms</span></div>
    <div class="summary-card"><strong>${activeCount}</strong><span>active</span></div>
    <div class="summary-card"><strong>${provisionalCount + rejectedCount}</strong><span>needs review</span></div>
  `;
}

function renderSessionList() {
  if (!state.sessions.length) {
    elements.sessionList.innerHTML = `<div class="empty-state">No stored sessions yet.</div>`;
    return;
  }
  elements.sessionList.innerHTML = "";
  for (const session of state.sessions) {
    const card = document.createElement("section");
    card.className = "session-card";
    card.innerHTML = `
      <div class="session-card-header">
        <div>
          <strong>${session.instrument_name || session.instrument_id}</strong>
          <div class="session-card-meta">${session.session_id}</div>
        </div>
        <span class="status-pill">${session.status}</span>
      </div>
      <div class="session-card-meta">
        responses ${session.response_count} | scores ${session.score_count} | atoms ${session.profile_atom_count}
      </div>
      <div class="session-card-meta">
        active ${session.active_atom_count} | confirmed ${session.confirmed_atom_count} | rejected ${session.rejected_atom_count}
      </div>
      <div class="session-actions-row">
        <button type="button" data-action="load">Load</button>
        <button type="button" data-action="export">Export</button>
        <button class="danger-button" type="button" data-action="delete">Delete</button>
      </div>
    `;
    card.querySelector("[data-action='load']").addEventListener("click", () => {
      loadSessionById(session.session_id).catch((error) => setAutosaveStatus(error.message, "warn"));
      switchView("administer");
    });
    card.querySelector("[data-action='export']").addEventListener("click", () => exportSession(session.session_id));
    card.querySelector("[data-action='delete']").addEventListener("click", () => {
      deleteSessionById(session.session_id).catch((error) => setAutosaveStatus(error.message, "warn"));
    });
    elements.sessionList.appendChild(card);
  }
}

function filteredWorkbenchAtoms() {
  const filter = elements.atomFilter.value;
  if (filter === "all") {
    return state.profileAtoms;
  }
  if (filter === "confirmed" || filter === "rejected") {
    return state.profileAtoms.filter((atom) => atom.user_feedback === filter);
  }
  return state.profileAtoms.filter((atom) => atom.state === filter);
}

function renderWorkbenchAtoms() {
  const atoms = filteredWorkbenchAtoms();
  if (!atoms.length) {
    elements.workbenchAtoms.innerHTML = `<div class="empty-state">No atoms match this filter.</div>`;
    return;
  }

  elements.workbenchAtoms.innerHTML = "";
  for (const atom of atoms) {
    const card = document.createElement("section");
    card.className = "atom-card";
    card.innerHTML = `
      <strong>${atom.label}</strong>
      <div class="atom-meta">
        ${atom.instrument_name || atom.instrument_id} | ${atom.session_id}
      </div>
      <div class="atom-meta">${atom.state} | ${atom.activation_scope} | feedback: ${atom.user_feedback}</div>
      <p>${atom.claim}</p>
      <div class="atom-meta">confidence ${atom.confidence} | sensitivity ${atom.sensitivity_level}</div>
      <div class="atom-actions">
        ${atomActionButton("Confirm", "confirmed")}
        ${atomActionButton("Reject", "rejected")}
        ${atomActionButton("Keep review-only", "review")}
      </div>
    `;
    card.querySelectorAll("button[data-action]").forEach((button) => {
      button.addEventListener("click", async () => {
        await applyAtomReview(atom.session_id, atom.id, button.dataset.action);
      });
    });
    elements.workbenchAtoms.appendChild(card);
  }
}

async function loadManifest() {
  state.manifest = await api("/api/manifest");
  renderManifest();
  if (!state.selectedInstrument && state.manifest.instruments.length > 0) {
    await loadInstrument(state.manifest.instruments[0].id);
  }
}

async function loadWorkbench() {
  const [sessionsPayload, atomsPayload] = await Promise.all([api("/api/sessions"), api("/api/profile-atoms")]);
  state.sessions = sessionsPayload.sessions || [];
  state.profileAtoms = atomsPayload.atoms || [];
  renderWorkbenchSummary();
  renderSessionList();
  renderWorkbenchAtoms();
}

async function loadInstrument(instrumentId) {
  state.selectedInstrument = await api(`/api/instruments/${encodeURIComponent(instrumentId)}`);
  state.session = null;
  elements.selectedInstrumentName.textContent = state.selectedInstrument.name;
  renderManifest();
  renderResponseScale(state.selectedInstrument);
  renderQuestionnaire();
  renderScores();
  renderAtoms();
  renderSessionMeta();
  setAutosaveStatus("Ready", "warn");
}

async function loadSessionById(sessionId) {
  state.session = await api(apiSessionPath(sessionId));
  state.selectedInstrument = await api(`/api/instruments/${encodeURIComponent(state.session.instrument_id)}`);
  elements.selectedInstrumentName.textContent = state.selectedInstrument.name;
  renderManifest();
  renderResponseScale(state.selectedInstrument);
  renderQuestionnaire();
  renderScores();
  renderAtoms();
  renderSessionMeta();
  setAutosaveStatus("Session loaded", "ok");
}

async function startSession() {
  if (!state.selectedInstrument) {
    return;
  }
  if (!elements.consentCheckbox.checked) {
    setAutosaveStatus("Consent required", "warn");
    return;
  }
  state.session = await api("/api/sessions", {
    method: "POST",
    body: JSON.stringify({ instrument_id: state.selectedInstrument.id }),
  });
  renderSessionMeta();
  renderQuestionnaire();
  setAutosaveStatus("Session started", "ok");
  await loadWorkbench();
}

function collectResponsesFromForm() {
  const responses = {};
  const items = flattenItems(state.selectedInstrument);
  for (const item of items) {
    const selected = elements.questionnaire.querySelector(`input[name="${item.id}"]:checked`);
    if (selected) {
      responses[item.id] = Number(selected.value);
    }
  }
  return responses;
}

async function persistResponses() {
  if (!state.session) {
    return;
  }
  const responses = collectResponsesFromForm();
  state.session = await api(apiSessionPath(state.session.session_id, "/responses"), {
    method: "POST",
    body: JSON.stringify({ responses, merge: false }),
  });
  renderSessionMeta();
  setAutosaveStatus(`Saved ${Object.keys(responses).length} responses`, "ok");
}

function onResponseChanged() {
  if (!state.session) {
    setAutosaveStatus("Start a session to save responses", "warn");
    return;
  }
  setAutosaveStatus("Saving...", "warn");
  window.clearTimeout(state.autosaveTimeout);
  state.autosaveTimeout = window.setTimeout(() => {
    persistResponses().catch((error) => setAutosaveStatus(error.message, "warn"));
  }, 250);
}

async function scoreCurrentSession() {
  if (!state.session) {
    return;
  }
  await persistResponses();
  state.session = await api(apiSessionPath(state.session.session_id, "/score"), {
    method: "POST",
    body: JSON.stringify({}),
  });
  renderSessionMeta();
  renderScores();
  renderAtoms();
  setAutosaveStatus("Scored", "ok");
  await loadWorkbench();
}

async function applyAtomReview(sessionId, atomId, action) {
  await api(apiSessionPath(sessionId, "/review-atom"), {
    method: "POST",
    body: JSON.stringify({
      atom_id: atomId,
      ...atomActionMapping(action),
    }),
  });
  if (state.session?.session_id === sessionId) {
    state.session = await api(apiSessionPath(sessionId));
    renderAtoms();
    renderSessionMeta();
  }
  await loadWorkbench();
  setAutosaveStatus("Atom state updated", "ok");
}

function exportSession(sessionId) {
  window.location.href = apiSessionPath(sessionId, "/export");
}

async function deleteSessionById(sessionId) {
  const confirmed = window.confirm(`Delete session ${sessionId}? This removes its responses, scores, and derived atoms from local JSONDB storage.`);
  if (!confirmed) {
    return;
  }
  await api(apiSessionPath(sessionId), { method: "DELETE" });
  if (state.session?.session_id === sessionId) {
    state.session = null;
    renderQuestionnaire();
    renderScores();
    renderAtoms();
    renderSessionMeta();
  }
  await loadWorkbench();
  setAutosaveStatus("Session deleted", "ok");
}

async function resumeSession() {
  const sessionId = elements.resumeSessionId.value.trim();
  if (!sessionId) {
    return;
  }
  await loadSessionById(sessionId);
}

elements.navAdminister.addEventListener("click", () => switchView("administer"));
elements.navWorkbench.addEventListener("click", () => switchView("workbench"));
elements.reloadManifest.addEventListener("click", () => loadManifest().catch((error) => setAutosaveStatus(error.message, "warn")));
elements.startSession.addEventListener("click", () => startSession().catch((error) => setAutosaveStatus(error.message, "warn")));
elements.scoreSession.addEventListener("click", () => scoreCurrentSession().catch((error) => setAutosaveStatus(error.message, "warn")));
elements.resumeSession.addEventListener("click", () => resumeSession().catch((error) => setAutosaveStatus(error.message, "warn")));
elements.refreshWorkbench.addEventListener("click", () => loadWorkbench().catch((error) => setAutosaveStatus(error.message, "warn")));
elements.atomFilter.addEventListener("change", renderWorkbenchAtoms);
elements.exportCurrentSession.addEventListener("click", () => {
  if (state.session) {
    exportSession(state.session.session_id);
  }
});
elements.deleteCurrentSession.addEventListener("click", () => {
  if (state.session) {
    deleteSessionById(state.session.session_id).catch((error) => setAutosaveStatus(error.message, "warn"));
  }
});

loadManifest().catch((error) => setAutosaveStatus(error.message, "warn"));
loadWorkbench().catch((error) => setAutosaveStatus(error.message, "warn"));
