import "./style.css";
import { RESOURCES, PAGE_SIZE } from "./config.js";
import { esc, toast } from "./utils.js";
import * as api from "./api.js";
import { readState, writeState } from "./url.js";
import { shellTemplate } from "./templates/shell.js";
import { recordItemTemplate } from "./templates/record.js";
import { detailTemplate, statusTemplate } from "./templates/detail.js";

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

  // Token field
  const input = document.querySelector("#token-input");
  input.value = api.getToken();
  document.querySelector("#token-toggle").addEventListener("click", () => {
    const btn = document.querySelector("#token-toggle");
    const visible = input.type === "text";
    input.type = visible ? "password" : "text";
    btn.innerHTML = `<i data-lucide="${visible ? "eye" : "eye-off"}"></i>`;
    if (window.lucide) lucide.createIcons({ nodes: [btn] });
  });
  document.querySelector("#token-save").addEventListener("click", saveToken);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") saveToken();
  });

  // Pagination + refresh
  document.querySelector("#page-prev").addEventListener("click", () => changePage(-1));
  document.querySelector("#page-next").addEventListener("click", () => changePage(1));
  document.querySelector("#refresh").addEventListener("click", () => loadCurrent());

  // Render lucide icons in the static shell
  if (window.lucide) lucide.createIcons();
}

function saveToken() {
  const value = document.querySelector("#token-input").value.trim();
  api.setToken(value);
  toast(value ? "Token saved" : "Token cleared");
  if (state.resource !== "status") loadCurrent();
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
 * Resource list (authenticated /api/v1/{resource})
 */
async function loadList() {
  const listEl = document.querySelector("#record-list");
  const countEl = document.querySelector("#list-count");
  const detail = document.querySelector("#detail-pane");

  if (!api.getToken()) {
    listEl.innerHTML = "";
    countEl.textContent = "0";
    detail.innerHTML = '<div class="empty">Paste a Bearer token above to browse this resource.</div>';
    updatePager();
    return;
  }

  listEl.innerHTML = '<div class="empty">Loading...</div>';
  try {
    const res = await api.fetchResource(state.resource, PAGE_SIZE, state.offset);
    if (res.status === 401) {
      listEl.innerHTML = "";
      countEl.textContent = "0";
      detail.innerHTML = '<div class="empty error">401 Unauthorized — token invalid or missing.</div>';
      updatePager();
      return;
    }
    if (!res.ok) {
      listEl.innerHTML = "";
      countEl.textContent = "0";
      detail.innerHTML = `<div class="empty error">${res.status} ${esc(res.statusText)} on /api/v1/${esc(state.resource)}</div>`;
      updatePager();
      return;
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
  document.querySelector("#detail-pane").innerHTML = detailTemplate(rec, state.view);
  document.querySelectorAll("#detail-pane .tab").forEach((tab) => {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab));
  });
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
 * Boot — restore view from the URL
 */
renderShell();
const initial = readState();
state.view = initial.view;
state.offset = initial.offset;
state.desiredUid = initial.uid;
selectResource(initial.tab, true);
syncBadges();
setInterval(syncBadges, 30000);
