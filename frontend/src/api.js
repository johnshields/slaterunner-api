import { TOKEN_KEY } from "./config.js";

/**
 * API client
 * Token storage, a shared request core, and generic resource CRUD keyed by
 * name so every /api/v1/{resource} is reachable without per-resource code.
 */

const BASE = "/api/v1";

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY) || "";
}

export function setToken(value) {
  if (value) {
    sessionStorage.setItem(TOKEN_KEY, value);
  } else {
    sessionStorage.removeItem(TOKEN_KEY);
  }
}

function authHeaders() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

/**
 * Shared request core. Returns the raw Response; callers own status handling.
 * A body implies JSON; auth headers are attached unless explicitly disabled.
 */
function request(method, path, { body, auth = true } = {}) {
  const headers = { ...(auth ? authHeaders() : {}) };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  return fetch(path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    redirect: "follow",
  });
}

/**
 * Status / auth.
 */
export function fetchStatus() {
  return request("GET", "/api", { auth: false }).then((res) => res.json());
}

export function verifyToken(token) {
  return fetch(`${BASE}/projects?limit=1&offset=0`, {
    headers: { Authorization: `Bearer ${token}` },
    redirect: "follow",
  }).then((res) => res.status);
}

/**
 * Generic resource CRUD (keyed by resource name).
 */
export function list(resource, limit, offset) {
  return request("GET", `${BASE}/${resource}?limit=${limit}&offset=${offset}`);
}

export function create(resource, body) {
  return request("POST", `${BASE}/${resource}`, { body });
}

export function update(resource, uid, body) {
  return request("PATCH", `${BASE}/${resource}/${encodeURIComponent(uid)}`, { body });
}

export function remove(resource, uid) {
  return request("DELETE", `${BASE}/${resource}/${encodeURIComponent(uid)}`);
}
