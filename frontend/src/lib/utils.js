/**
 * Pure formatting helpers
 * Stateless string transforms; no persistent DOM or domain knowledge.
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
