import { RESOURCES, PAGE_SIZE } from "./config.js";
import { esc, toast, icons, primaryLabel } from "./utils.js";
import { api } from "./api.js";
import { readState, writeState } from "./url.js";
import { RESOURCE_MODELS, WRITABLE, formDef, relationships } from "./forms.js";
import { Modal } from "./ui/modal.js";
import { ResourceForm } from "./ui/resource-form.js";
import { shellTemplate } from "./templates/shell.js";
import { gateTemplate } from "./templates/gate.js";
import { recordItemTemplate } from "./templates/record.js";
import { detailTemplate, statusTemplate } from "./templates/detail.js";
import { confirmBody } from "./templates/modal.js";

const BADGE_INTERVAL = 30000;

/**
 * Console
 * Controller for the SlateRunner admin console. Owns view state, drives the
 * login gate, list/detail views and resource CRUD, and mirrors view state into
 * the query string (see url.js) so refresh and shared links restore the page.
 * Stateless markup lives in templates/; reusable behaviour in ui/.
 */
export class Console {
  #state = {
    resource: "status",
    offset: 0,
    count: 0,
    records: [],
    activeIndex: null,
    view: "fields",
    desiredUid: null,
  };

  #modal = new Modal();
  #badgesStarted = false;
  #children = {};

  /**
   * Boot — gate first, validate any stored token.
   */
  async boot() {
    const stored = api.token;
    if (stored && (await api.verify(stored).catch(() => 0)) === 200) {
      this.#start();
    } else {
      if (stored) api.token = "";
      this.#renderGate();
    }
  }

  /**
   * Login gate
   */
  #renderGate() {
    const app = document.querySelector("#app");
    app.className = "app";
    app.innerHTML = gateTemplate();
    icons();

    const input = document.querySelector("#gate-input");
    document.querySelector("#gate-exec").addEventListener("click", () => this.#login());
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") this.#login();
    });
    input.focus();
  }

  async #login() {
    const input = document.querySelector("#gate-input");
    const error = document.querySelector("#gate-error");
    const value = input.value.trim();
    if (!value) return;

    const status = await api.verify(value).catch(() => 0);
    if (status === 200) {
      api.token = value;
      this.#start();
      return;
    }
    error.textContent = status === 401 ? "Access denied" : "Connection error";
    error.style.display = "block";
    input.value = "";
    input.focus();
  }

  #logout() {
    api.token = "";
    toast("Locked");
    this.#renderGate();
  }

  /**
   * Console — render shell and restore view from the URL.
   */
  async #start() {
    this.#renderShell();
    this.#children = await relationships().catch(() => ({}));
    const initial = readState();
    this.#state.view = initial.view;
    this.#state.offset = initial.offset;
    this.#state.desiredUid = initial.uid;
    this.#selectResource(initial.tab, true);
    if (!this.#badgesStarted) {
      this.#syncBadges();
      setInterval(() => this.#syncBadges(), BADGE_INTERVAL);
      this.#badgesStarted = true;
    }
  }

  #renderShell() {
    const app = document.querySelector("#app");
    app.className = "app";
    app.innerHTML = shellTemplate();

    const rail = document.querySelector("#nav-rail");
    rail.innerHTML = RESOURCES.map((r, i) => {
      const sep = i === 1 ? '<div class="nav-sep"></div>' : "";
      return `${sep}<div class="nav-item" data-key="${r.key}">${esc(r.label)}</div>`;
    }).join("");
    rail.querySelectorAll(".nav-item").forEach((el) => {
      el.addEventListener("click", () => this.#selectResource(el.dataset.key));
    });

    document.querySelector("#logout").addEventListener("click", () => this.#logout());
    document.querySelector("#create").addEventListener("click", () => this.#openForm(this.#state.resource, null));
    document.querySelector("#page-prev").addEventListener("click", () => this.#changePage(-1));
    document.querySelector("#page-next").addEventListener("click", () => this.#changePage(1));
    document.querySelector("#refresh").addEventListener("click", () => this.#loadCurrent());

    // Copy JSON (delegated; the detail pane is re-rendered on every selection)
    document.querySelector("#detail-pane").addEventListener("click", (e) => {
      const btn = e.target.closest(".copy-btn");
      if (!btn) return;
      navigator.clipboard.writeText(btn.parentElement.querySelector("pre").textContent);
      toast("Copied");
    });

    icons();
  }

  /**
   * Navigation
   * restore=true keeps the offset/uid carried in from the URL on boot;
   * otherwise a fresh resource selection resets paging and selection.
   */
  #selectResource(key, restore = false) {
    this.#state.resource = key;
    if (!restore) {
      this.#state.offset = 0;
      this.#state.desiredUid = null;
      this.#state.activeIndex = null;
    }
    document.querySelectorAll(".nav-item").forEach((el) => {
      el.classList.toggle("active", el.dataset.key === key);
    });
    document.querySelector("#app").classList.toggle("status-view", key === "status");
    document.querySelector("#create").hidden = !WRITABLE.has(key);
    this.#syncUrl();
    this.#loadCurrent();
  }

  #changePage(direction) {
    const next = this.#state.offset + direction * PAGE_SIZE;
    if (next < 0 || next >= this.#state.count) return;
    this.#state.offset = next;
    this.#state.desiredUid = null;
    this.#loadList();
  }

  #loadCurrent() {
    return this.#state.resource === "status" ? this.#loadStatus() : this.#loadList();
  }

  /**
   * Status view (unauthenticated /api)
   */
  async #loadStatus() {
    const detail = document.querySelector("#detail-pane");
    detail.innerHTML = '<div class="empty">Loading status...</div>';
    try {
      detail.innerHTML = statusTemplate(await api.status());
      icons();
    } catch (err) {
      detail.innerHTML = `<div class="empty error">Failed to load /api<br>${esc(err.message)}</div>`;
    }
  }

  /**
   * Resource list (authenticated /api/v1/{resource})
   */
  async #loadList() {
    const listEl = document.querySelector("#record-list");
    listEl.innerHTML = '<div class="empty">Loading...</div>';
    try {
      const res = await api.list(this.#state.resource, PAGE_SIZE, this.#state.offset);
      if (res.status === 401) {
        return this.#showListMessage('<div class="empty error">401 Unauthorized — token invalid or missing.</div>');
      }
      if (!res.ok) {
        return this.#showListMessage(`<div class="empty error">${res.status} ${esc(res.statusText)} on /api/v1/${esc(this.#state.resource)}</div>`);
      }
      const json = await res.json();
      this.#state.records = json.data || [];
      this.#state.count = json.count ?? this.#state.records.length;
      this.#renderList();
    } catch (err) {
      listEl.innerHTML = `<div class="empty error">${esc(err.message)}</div>`;
    }
  }

  #showListMessage(html) {
    document.querySelector("#record-list").innerHTML = "";
    document.querySelector("#list-count").textContent = "0";
    document.querySelector("#detail-pane").innerHTML = html;
    this.#updatePager();
  }

  #renderList() {
    const { records, count, offset } = this.#state;
    const listEl = document.querySelector("#record-list");
    const countEl = document.querySelector("#list-count");
    const detail = document.querySelector("#detail-pane");

    const from = count === 0 ? 0 : offset + 1;
    countEl.textContent = `${from}–${offset + records.length} of ${count}`;
    this.#updatePager();

    if (records.length === 0) {
      listEl.innerHTML = '<div class="empty">No records.</div>';
      detail.innerHTML = '<div class="empty muted">Nothing to show.</div>';
      return;
    }

    listEl.innerHTML = records.map((rec, i) => recordItemTemplate(rec, i)).join("");
    listEl.querySelectorAll(".record-item").forEach((el) => {
      el.addEventListener("click", () => this.#selectRecord(Number(el.dataset.index)));
    });

    // Restore the record named in the URL, else fall back to the first
    let index = 0;
    if (this.#state.desiredUid) {
      const found = records.findIndex((r) => r.uid === this.#state.desiredUid);
      if (found >= 0) index = found;
    }
    this.#state.desiredUid = null;
    this.#selectRecord(index);
  }

  #updatePager() {
    document.querySelector("#page-prev").disabled = this.#state.offset <= 0;
    document.querySelector("#page-next").disabled = this.#state.offset + PAGE_SIZE >= this.#state.count;
  }

  #selectRecord(index) {
    this.#state.activeIndex = index;
    document.querySelectorAll(".record-item").forEach((el) => {
      el.classList.toggle("active", Number(el.dataset.index) === index);
    });
    this.#renderDetail(this.#state.records[index]);
    this.#syncUrl();
  }

  #renderDetail(rec) {
    const writable = WRITABLE.has(this.#state.resource);
    const children = this.#children[this.#state.resource] || [];
    document.querySelector("#detail-pane").innerHTML = detailTemplate(rec, this.#state.view, writable, children.length > 0);
    icons();
    document.querySelectorAll("#detail-pane .tab").forEach((tab) => {
      tab.addEventListener("click", () => this.#switchTab(tab.dataset.tab));
    });
    if (children.length) {
      document.querySelector("#add-child").addEventListener("click", () => this.#chooseChild(rec, children));
    }
    if (writable) {
      document.querySelector("#edit-record").addEventListener("click", () => this.#openForm(this.#state.resource, rec));
      document.querySelector("#delete-record").addEventListener("click", () => this.#confirmDelete(rec));
    }
  }

  /**
   * Offer the child types that reference this record; opening one pre-fills the
   * foreign key with the parent's uid.
   */
  #chooseChild(record, children) {
    const body = `<div class="child-list">${children
      .map((c) => `<button class="modal-btn child-opt" data-resource="${c.resource}" data-fk="${esc(c.fkKey)}">New ${esc(c.noun)}</button>`)
      .join("")}</div>`;

    this.#modal.open({ title: "Create related", body, footer: false });
    this.#modal.body.querySelectorAll(".child-opt").forEach((btn) => {
      btn.addEventListener("click", () => {
        this.#openForm(btn.dataset.resource, null, { [btn.dataset.fk]: record.uid });
      });
    });
  }

  #switchTab(name) {
    this.#state.view = name;
    document.querySelectorAll("#detail-pane .tab").forEach((t) => {
      t.classList.toggle("active", t.dataset.tab === name);
    });
    document.querySelectorAll("#detail-pane .tab-content").forEach((c) => {
      c.classList.toggle("active", c.dataset.pane === name);
    });
    this.#syncUrl();
  }

  /**
   * Resource CRUD
   */
  async #openForm(resource, record, prefill = null) {
    let def;
    try {
      def = await formDef(resource);
    } catch {
      return toast("Could not load form schema", "error");
    }
    const form = new ResourceForm(def);
    const editing = Boolean(record);

    this.#modal.open({
      title: `${editing ? "Edit" : "New"} ${form.noun}`,
      body: form.render(record || prefill),
      confirmLabel: editing ? "Save" : "Create",
      onConfirm: () => this.#submitForm(form, resource, record),
    });

    this.#modal.body.querySelector("input, select, textarea")?.focus();
    this.#modal.body.querySelectorAll("input").forEach((inp) => {
      inp.addEventListener("keydown", (e) => {
        if (e.key === "Enter") this.#submitForm(form, resource, record);
      });
    });
  }

  async #submitForm(form, resource, record) {
    let body;
    try {
      body = form.collect();
    } catch (e) {
      return this.#modal.setError(e.message);
    }

    const res = record ? await api.update(resource, record.uid, body) : await api.create(resource, body);
    if (!res.ok) return this.#modal.setError(await this.#writeError(res));

    const json = await res.json().catch(() => null);
    this.#modal.close();
    toast(record ? "Updated" : "Created");
    this.#reloadAfterWrite(record ? record.uid : json?.data?.uid);
  }

  #confirmDelete(record) {
    const noun = RESOURCE_MODELS[this.#state.resource].noun;
    this.#modal.open({
      title: `Delete ${noun}`,
      body: confirmBody(`Delete "${primaryLabel(record)}"? It will be removed from the ${noun} list.`),
      confirmLabel: "Delete",
      danger: true,
      onConfirm: async () => {
        const res = await api.remove(this.#state.resource, record.uid);
        if (!res.ok) return this.#modal.setError(await this.#writeError(res));
        this.#modal.close();
        toast("Deleted");
        this.#reloadAfterWrite(null);
      },
    });
  }

  async #writeError(res) {
    if (res.status === 401) return "Unauthorized — token invalid.";
    const data = await res.json().catch(() => null);
    return data?.message || data?.detail || `Error ${res.status}`;
  }

  /**
   * Reload the list after a write, reselecting the affected record.
   */
  #reloadAfterWrite(uid) {
    this.#state.desiredUid = uid || null;
    this.#loadList();
  }

  /**
   * Topbar status badges (poll /api)
   */
  async #syncBadges() {
    try {
      const data = await api.status();
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
   * URL state
   */
  #syncUrl() {
    writeState({
      tab: this.#state.resource,
      uid: this.#currentUid(),
      view: this.#state.view,
      offset: this.#state.offset,
    });
  }

  #currentUid() {
    if (this.#state.resource === "status") return null;
    const rec = this.#state.records[this.#state.activeIndex];
    return (rec && rec.uid) || this.#state.desiredUid || null;
  }
}
