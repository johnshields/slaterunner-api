import { TOKEN_KEY } from "./config.js";

/**
 * API client
 * Token storage, a shared request core, and generic resource CRUD keyed by
 * name so every /api/v1/{resource} is reachable without per-resource code.
 */
class Api {
  #base = "/api/v1";
  #schema = null;

  get token() {
    return sessionStorage.getItem(TOKEN_KEY) || "";
  }

  set token(value) {
    if (value) {
      sessionStorage.setItem(TOKEN_KEY, value);
    } else {
      sessionStorage.removeItem(TOKEN_KEY);
    }
  }

  #authHeaders() {
    return this.token ? { Authorization: `Bearer ${this.token}` } : {};
  }

  /**
   * Shared request core. Returns the raw Response; callers own status handling.
   * A body implies JSON; auth headers attach unless explicitly disabled.
   */
  #request(method, path, { body, auth = true } = {}) {
    const headers = { ...(auth ? this.#authHeaders() : {}) };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    return fetch(path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      redirect: "follow",
    });
  }

  status() {
    return this.#request("GET", "/api", { auth: false }).then((res) => res.json());
  }

  /**
   * The OpenAPI document, fetched once and cached. Source of truth for forms.
   */
  async schema() {
    if (!this.#schema) {
      this.#schema = await fetch("/openapi.json", { redirect: "follow" }).then((res) => res.json());
    }
    return this.#schema;
  }

  verify(token) {
    return fetch(`${this.#base}/projects?limit=1&offset=0`, {
      headers: { Authorization: `Bearer ${token}` },
      redirect: "follow",
    }).then((res) => res.status);
  }

  list(resource, limit, offset) {
    return this.#request("GET", `${this.#base}/${resource}?limit=${limit}&offset=${offset}`);
  }

  create(resource, body) {
    return this.#request("POST", `${this.#base}/${resource}`, { body });
  }

  update(resource, uid, body) {
    return this.#request("PATCH", `${this.#base}/${resource}/${encodeURIComponent(uid)}`, { body });
  }

  remove(resource, uid) {
    return this.#request("DELETE", `${this.#base}/${resource}/${encodeURIComponent(uid)}`);
  }
}

export const api = new Api();
