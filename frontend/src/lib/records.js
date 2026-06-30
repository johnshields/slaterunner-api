import { esc } from "./utils.js";

/**
 * Record presentation
 * Schema-agnostic helpers for displaying pipeline records.
 */

/**
 * Pick a human label for a record without knowing its exact schema.
 */
export function primaryLabel(rec) {
  const keys = ["name", "code", "label", "title", "shot", "task", "key"];
  for (const k of keys) {
    if (rec[k]) return rec[k];
  }
  return rec.uid || rec.id || "(record)";
}

export function secondaryLabel(rec) {
  return rec.uid || rec.created_at || rec.updated_at || "";
}

/**
 * Map a status value to a semantic pill tone.
 */
const STATUS_TONE = {
  succeeded: "success",
  approved: "success",
  done: "success",
  running: "info",
  wip: "info",
  ready: "success",
  review: "warning",
  hold: "warning",
  failed: "danger",
  rejected: "danger",
  queued: "neutral",
  draft: "neutral",
};

export function statusPill(rec) {
  const v = rec.status || rec.state;
  if (!v) return "";
  const tone = STATUS_TONE[String(v).toLowerCase()] || "neutral";
  return `<span class="pill pill-${tone}">${esc(v)}</span>`;
}
