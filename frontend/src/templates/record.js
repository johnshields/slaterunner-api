import { esc } from "../utils.js";
import { primaryLabel, secondaryLabel, statusPill } from "../records.js";

/**
 * List + table templates
 */

export function recordItemTemplate(rec, index) {
  return `
    <div class="record-item" data-index="${index}">
      <div class="record-row">
        <span class="record-primary">${esc(primaryLabel(rec))}</span>
        ${statusPill(rec)}
      </div>
      <div class="record-secondary">${esc(secondaryLabel(rec))}</div>
    </div>`;
}

/**
 * Render scalar fields of an object as a table; nested values fall back to JSON.
 */
export function fieldsTable(obj) {
  const rows = Object.entries(obj)
    .map(([k, v]) => {
      const display =
        v !== null && typeof v === "object" ? `<span class="muted">${esc(JSON.stringify(v))}</span>` : esc(v);
      return `<tr><td>${esc(k)}</td><td>${display}</td></tr>`;
    })
    .join("");
  return `<table class="fields-table"><tbody>${rows}</tbody></table>`;
}
