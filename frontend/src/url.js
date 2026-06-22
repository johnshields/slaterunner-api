import { RESOURCES } from "./config.js";

/**
 * URL state
 * Mirrors the active view into the query string so a refresh or shared link
 * restores the same resource, record, detail tab and page.
 *   ?tab=events&event_uid=EVN_PUB001&view=json&offset=50
 */

const BY_KEY = Object.fromEntries(RESOURCES.map((r) => [r.key, r]));

export function uidParamFor(resourceKey) {
  return BY_KEY[resourceKey]?.uidParam || "uid";
}

export function readState() {
  const p = new URLSearchParams(location.search);
  const requested = p.get("tab");
  const tab = requested && BY_KEY[requested] ? requested : "status";
  return {
    tab,
    uid: p.get(uidParamFor(tab)) || null,
    view: p.get("view") === "json" ? "json" : "fields",
    offset: Math.max(0, parseInt(p.get("offset"), 10) || 0),
  };
}

export function writeState({ tab, uid, view, offset }) {
  const p = new URLSearchParams();
  p.set("tab", tab);
  if (offset > 0) p.set("offset", String(offset));
  if (uid) {
    p.set(uidParamFor(tab), uid);
    if (view) p.set("view", view);
  }
  const qs = p.toString();
  history.replaceState(null, "", qs ? `/?${qs}` : "/");
}
