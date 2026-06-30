import { TOKEN_KEY } from "./config.js";

/**
 * API client
 * Token storage plus thin fetch wrappers. Returns raw Responses so the
 * controller stays in charge of status handling and DOM updates.
 */

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

export function authHeaders() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

export function fetchStatus() {
  return fetch("/api", { redirect: "follow" }).then((res) => res.json());
}

export function fetchResource(resource, limit, offset) {
  const url = `/api/v1/${resource}?limit=${limit}&offset=${offset}`;
  return fetch(url, { headers: authHeaders(), redirect: "follow" });
}

/**
 * Validate a candidate token against an authenticated endpoint.
 * Resolves to the HTTP status (200 valid, 401 denied).
 */
export function verifyToken(token) {
  return fetch("/api/v1/projects?limit=1&offset=0", {
    headers: { Authorization: `Bearer ${token}` },
    redirect: "follow",
  }).then((res) => res.status);
}
