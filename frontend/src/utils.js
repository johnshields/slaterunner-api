/**
 * Pure helpers
 * No DOM mutation beyond throwaway nodes; safe to reuse anywhere.
 */

export function esc(s) {
  if (s === null || s === undefined) return "";
  const d = document.createElement("div");
  d.textContent = String(s);
  return d.innerHTML;
}

export function colorJson(value) {
  const raw = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  const str = raw.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return str
    .replace(/(".*?")\s*:/g, '<span class="rk">$1</span>:')
    .replace(/:\s*(".*?")/g, ': <span class="rv">$1</span>')
    .replace(/:\s*(-?\d+\.?\d*)(?=\s*[,\n\r\]}])/g, ': <span class="rn">$1</span>')
    .replace(/:\s*(true|false|null)/g, ': <span class="rv">$1</span>');
}

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

export function statusPill(rec) {
  const v = rec.status || rec.state;
  return v ? `<span class="pill">${esc(v)}</span>` : "";
}

export function icons() {
  if (window.lucide) window.lucide.createIcons();
}

export function toast(message, type = "success") {
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = message;
  document.body.appendChild(el);
  requestAnimationFrame(() => el.classList.add("show"));
  setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => el.remove(), 300);
  }, 2200);
}
