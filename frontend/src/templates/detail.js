import { esc, colorJson, primaryLabel } from "../utils.js";
import { fieldsTable } from "./record.js";

/**
 * Detail-pane templates
 */

export function detailTemplate(rec, view = "fields") {
  const json = view === "json";
  return `
    <div class="detail-header">${esc(primaryLabel(rec))}</div>
    <div class="tabs">
      <button class="tab ${json ? "" : "active"}" data-tab="fields">Fields</button>
      <button class="tab ${json ? "active" : ""}" data-tab="json">JSON</button>
    </div>
    <div class="tab-content ${json ? "" : "active"}" data-pane="fields">${fieldsTable(rec)}</div>
    <div class="tab-content ${json ? "active" : ""}" data-pane="json"><pre class="code-block">${colorJson(rec)}</pre></div>
  `;
}

export function statusTemplate(data) {
  return `
    <div class="detail-header">Service status</div>
    ${fieldsTable(data)}
    <pre class="code-block">${colorJson(data)}</pre>
  `;
}
