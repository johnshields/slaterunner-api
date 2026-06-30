import { esc, colorJson, primaryLabel } from "../utils.js";
import { fieldsTable } from "./record.js";

/**
 * Detail-pane templates
 */

/**
 * A JSON code block with a copy button. The raw JSON is recoverable from the
 * <pre> text content, so the copy handler reads it directly.
 */
function jsonBlock(value) {
  return `
    <div class="code-wrap">
      <button class="btn-icon copy-btn" title="Copy JSON"><i data-lucide="copy"></i></button>
      <pre class="code-block">${colorJson(value)}</pre>
    </div>`;
}

export function detailTemplate(rec, view = "fields", actions = false) {
  const json = view === "json";
  const actionBtns = actions
    ? `<div class="detail-actions">
        <button class="btn-icon" id="edit-record" title="Edit"><i data-lucide="pencil"></i></button>
        <button class="btn-icon" id="delete-record" title="Delete"><i data-lucide="trash-2"></i></button>
      </div>`
    : "";
  return `
    <div class="detail-header"><span>${esc(primaryLabel(rec))}</span>${actionBtns}</div>
    <div class="tabs">
      <button class="tab ${json ? "" : "active"}" data-tab="fields">Fields</button>
      <button class="tab ${json ? "active" : ""}" data-tab="json">JSON</button>
    </div>
    <div class="tab-content ${json ? "" : "active"}" data-pane="fields">${fieldsTable(rec)}</div>
    <div class="tab-content ${json ? "active" : ""}" data-pane="json">${jsonBlock(rec)}</div>
  `;
}

export function statusTemplate(data) {
  return `
    <div class="detail-header">Service status</div>
    ${fieldsTable(data)}
    ${jsonBlock(data)}
  `;
}
