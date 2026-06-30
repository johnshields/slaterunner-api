import "./style.css";
import { RESOURCES, PAGE_SIZE } from "./config.js";
import { esc, toast, icons } from "./utils.js";
import * as api from "./api.js";
import { readState, writeState } from "./url.js";
import { shellTemplate } from "./templates/shell.js";
import { gateTemplate } from "./templates/gate.js";
import { recordItemTemplate } from "./templates/record.js";
import { detailTemplate, statusTemplate } from "./templates/detail.js";
import { modalTemplate, projectFormBody, confirmBody } from "./templates/modal.js";

/**
 * Resources that support write operations from the console.
 */
const WRITABLE = new Set(["projects"]);

/**
 * SlateRunner console controller
 * Read-only browser over the /api/v1 pipeline resources, served by FastAPI
 * via app.frontend(). Status view integrates the public /api payload.
 * View state is mirrored into the query string (see url.js) so refresh and
 * shared links restore the same resource, record, tab and page.
 * Design language adapted from the hookblade inspector.
 */

const state = {
  resource: "status",
  offset: 0,
  count: 0,
  records: [],
  activeIndex: null,
  view: "fields",
  desiredUid: null,
};

/**
 * Reflect current state into the URL.
 */
function syncUrl() {
  writeState({
    tab: state.resource,
    uid: currentUid(),
    view: state.view,
    offset: state.offset,
  });
}

function currentUid() {
  if (state.resource === "status") return null;
  const rec = state.records[state.activeIndex];
  return (rec && rec.uid) || state.desiredUid || null;
}

/**
 * Shell render (once)
 */
function renderShell() {
  const app = document.querySelector("#app");
  app.className = "app";
  app.innerHTML = shellTemplate();

  // Nav rail
  const rail = document.querySelector("#nav-rail");
  rail.innerHTML = RESOURCES.map((r, i) => {
    const sep = i === 1 ? '<div class="nav-sep"></div>' : "";
    return `${sep}<div class="nav-item" data-key="${r.key}">${esc(r.label)}</div>`;
  }).join("");
  rail.querySelectorAll(".nav-item").forEach((el) => {
    el.addEventListener("click", () => selectResource(el.dataset.key));
  });

  // Logout
  document.querySelector("#logout").addEventListener("click", logout);

  // Create
  document.querySelector("#create").addEventListener("click", () => openProjectForm(null));

  // Pagination + refresh
  document.querySelector("#page-prev").addEventListener("click", () => changePage(-1));
  document.querySelector("#page-next").addEventListener("click", () => changePage(1));
  document.querySelector("#refresh").addEventListener("click", () => loadCurrent());

  // Render lucide icons in the static shell
  icons();
}

/**
 * Login gate
 */
function renderGate() {
  const app = document.querySelector("#app");
  app.className = "app";
  app.innerHTML = gateTemplate();
  icons();

  const input = document.querySelector("#gate-input");
  document.querySelector("#gate-exec").addEventListener("click", login);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") login();
  });
  input.focus();
}

async function login() {
  const input = document.querySelector("#gate-input");
  const error = document.querySelector("#gate-error");
  const value = input.value.trim();
  if (!value) return;

  const status = await api.verifyToken(value).catch(() => 0);
  if (status === 200) {
    api.setToken(value);
    startConsole();
    return;
  }
  error.textContent = status === 401 ? "Access denied" : "Connection error";
  error.style.display = "block";
  input.value = "";
  input.focus();
}

function logout() {
  api.setToken("");
  toast("Locked");
  renderGate();
}

/**
 * Navigation
 * restore=true keeps the offset/uid carried in from the URL on boot;
 * otherwise a fresh resource selection resets paging and selection.
 */
function selectResource(key, restore = false) {
  state.resource = key;
  if (!restore) {
    state.offset = 0;
    state.desiredUid = null;
    state.activeIndex = null;
  }
  document.querySelectorAll(".nav-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.key === key);
  });
  document.querySelector("#app").classList.toggle("status-view", key === "status");
  document.querySelector("#create").hidden = !WRITABLE.has(key);
  syncUrl();
  loadCurrent();
}

function changePage(direction) {
  const next = state.offset + direction * PAGE_SIZE;
  if (next < 0 || next >= state.count) return;
  state.offset = next;
  state.desiredUid = null;
  loadList();
}

function loadCurrent() {
  return state.resource === "status" ? loadStatus() : loadList();
}

/**
 * Status view (unauthenticated /api)
 */
async function loadStatus() {
  const detail = document.querySelector("#detail-pane");
  detail.innerHTML = '<div class="empty">Loading status...</div>';
  try {
    detail.innerHTML = statusTemplate(await api.fetchStatus());
  } catch (err) {
    detail.innerHTML = `<div class="empty error">Failed to load /api<br>${esc(err.message)}</div>`;
  }
}

/**
 * Clear the list and surface a message in the detail pane.
 */
function showListMessage(html) {
  document.querySelector("#record-list").innerHTML = "";
  document.querySelector("#list-count").textContent = "0";
  document.querySelector("#detail-pane").innerHTML = html;
  updatePager();
}

/**
 * Resource list (authenticated /api/v1/{resource})
 */
async function loadList() {
  const listEl = document.querySelector("#record-list");
  listEl.innerHTML = '<div class="empty">Loading...</div>';
  try {
    const res = await api.list(state.resource, PAGE_SIZE, state.offset);
    if (res.status === 401) {
      return showListMessage('<div class="empty error">401 Unauthorized — token invalid or missing.</div>');
    }
    if (!res.ok) {
      return showListMessage(`<div class="empty error">${res.status} ${esc(res.statusText)} on /api/v1/${esc(state.resource)}</div>`);
    }
    const json = await res.json();
    state.records = json.data || [];
    state.count = json.count ?? state.records.length;
    renderList();
  } catch (err) {
    listEl.innerHTML = `<div class="empty error">${esc(err.message)}</div>`;
  }
}

function renderList() {
  const listEl = document.querySelector("#record-list");
  const countEl = document.querySelector("#list-count");
  const detail = document.querySelector("#detail-pane");

  const from = state.count === 0 ? 0 : state.offset + 1;
  const to = state.offset + state.records.length;
  countEl.textContent = `${from}–${to} of ${state.count}`;
  updatePager();

  if (state.records.length === 0) {
    listEl.innerHTML = '<div class="empty">No records.</div>';
    detail.innerHTML = '<div class="empty muted">Nothing to show.</div>';
    return;
  }

  listEl.innerHTML = state.records.map((rec, i) => recordItemTemplate(rec, i)).join("");
  listEl.querySelectorAll(".record-item").forEach((el) => {
    el.addEventListener("click", () => selectRecord(Number(el.dataset.index)));
  });

  // Restore the record named in the URL, else fall back to the first
  let index = 0;
  if (state.desiredUid) {
    const found = state.records.findIndex((r) => r.uid === state.desiredUid);
    if (found >= 0) index = found;
  }
  state.desiredUid = null;
  selectRecord(index);
}

function updatePager() {
  document.querySelector("#page-prev").disabled = state.offset <= 0;
  document.querySelector("#page-next").disabled = state.offset + PAGE_SIZE >= state.count;
}

function selectRecord(index) {
  state.activeIndex = index;
  document.querySelectorAll(".record-item").forEach((el) => {
    el.classList.toggle("active", Number(el.dataset.index) === index);
  });
  renderDetail(state.records[index]);
  syncUrl();
}

function renderDetail(rec) {
  const writable = WRITABLE.has(state.resource);
  document.querySelector("#detail-pane").innerHTML = detailTemplate(rec, state.view, writable);
  icons();
  document.querySelectorAll("#detail-pane .tab").forEach((tab) => {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab));
  });
  if (writable) {
    document.querySelector("#edit-record").addEventListener("click", () => openProjectForm(rec));
    document.querySelector("#delete-record").addEventListener("click", () => confirmDelete(rec));
  }
}

function switchTab(name) {
  state.view = name;
  document.querySelectorAll("#detail-pane .tab").forEach((t) => {
    t.classList.toggle("active", t.dataset.tab === name);
  });
  document.querySelectorAll("#detail-pane .tab-content").forEach((c) => {
    c.classList.toggle("active", c.dataset.pane === name);
  });
  syncUrl();
}

/**
 * Topbar status badges (poll /api)
 */
async function syncBadges() {
  try {
    const data = await api.fetchStatus();
    if (data.version !== undefined) {
      document.querySelector("#version-badge").textContent = `v${data.version}`;
    }
    if (data.uptime_seconds !== undefined) {
      document.querySelector("#uptime-badge").textContent = `Uptime: ${data.uptime_seconds}s`;
    }
  } catch {
    document.querySelector("#uptime-badge").textContent = "Uptime: error";
  }
}

/**
 * Modal infrastructure
 */
function openModal(html) {
  closeModal();
  const root = document.createElement("div");
  root.id = "modal-root";
  root.innerHTML = html;
  document.body.appendChild(root);
  icons();

  const overlay = document.querySelector("#modal-overlay");
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal();
  });
  document.querySelector("#modal-close").addEventListener("click", closeModal);
  document.querySelector("#modal-cancel").addEventListener("click", closeModal);
  document.addEventListener("keydown", escClose);
}

function closeModal() {
  document.removeEventListener("keydown", escClose);
  document.querySelector("#modal-root")?.remove();
}

function escClose(e) {
  if (e.key === "Escape") closeModal();
}

function modalError(message) {
  const el = document.querySelector("#modal-error");
  if (el) el.textContent = message;
}

async function writeError(res) {
  if (res.status === 401) return "Unauthorized — token invalid.";
  const data = await res.json().catch(() => null);
  return data?.message || data?.detail || `Error ${res.status}`;
}

/**
 * Reload the list after a write, reselecting the affected record.
 */
function reloadAfterWrite(uid) {
  state.desiredUid = uid || null;
  loadList();
}

/**
 * Project create / edit / delete
 */
function openProjectForm(project) {
  const editing = Boolean(project);
  openModal(
    modalTemplate({
      title: editing ? "Edit project" : "New project",
      body: projectFormBody(project),
      confirmLabel: editing ? "Save" : "Create",
    })
  );
  const input = document.querySelector("#field-name");
  input.focus();
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") submitProject(project);
  });
  document.querySelector("#modal-confirm").addEventListener("click", () => submitProject(project));
}

async function submitProject(project) {
  const name = document.querySelector("#field-name").value.trim();
  if (!name) return modalError("Name is required.");

  const res = project
    ? await api.update("projects", project.uid, { name })
    : await api.create("projects", { name });

  if (!res.ok) return modalError(await writeError(res));

  const json = await res.json().catch(() => null);
  closeModal();
  toast(project ? "Project updated" : "Project created");
  reloadAfterWrite(project ? project.uid : json?.data?.uid);
}

function confirmDelete(project) {
  openModal(
    modalTemplate({
      title: "Delete project",
      body: confirmBody(`Delete "${project.name}"? This soft-deletes the project.`),
      confirmLabel: "Delete",
      danger: true,
    })
  );
  document.querySelector("#modal-confirm").addEventListener("click", async () => {
    const res = await api.remove("projects", project.uid);
    if (!res.ok) return modalError(await writeError(res));
    closeModal();
    toast("Project deleted");
    reloadAfterWrite(null);
  });
}

/**
 * Console — render shell and restore view from the URL
 */
let badgesStarted = false;
function startConsole() {
  renderShell();
  const initial = readState();
  state.view = initial.view;
  state.offset = initial.offset;
  state.desiredUid = initial.uid;
  selectResource(initial.tab, true);
  if (!badgesStarted) {
    syncBadges();
    setInterval(syncBadges, 30000);
    badgesStarted = true;
  }
}

/**
 * Boot — gate first, validate any stored token
 */
async function boot() {
  const stored = api.getToken();
  if (stored && (await api.verifyToken(stored).catch(() => 0)) === 200) {
    startConsole();
  } else {
    if (stored) api.setToken("");
    renderGate();
  }
}

boot();
