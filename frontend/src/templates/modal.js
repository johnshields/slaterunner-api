import { esc } from "../utils.js";

/**
 * Modal templates
 * Generic overlay + dialog, plus per-purpose body builders.
 */

export function modalTemplate({ title, body, confirmLabel = "Save", danger = false }) {
  return `
    <div class="modal-overlay" id="modal-overlay">
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal-header">
          <span>${esc(title)}</span>
          <button class="btn-icon" id="modal-close" title="Close"><i data-lucide="x"></i></button>
        </div>
        <div class="modal-body">${body}</div>
        <div class="modal-error" id="modal-error"></div>
        <div class="modal-actions">
          <button class="modal-btn" id="modal-cancel" type="button">Cancel</button>
          <button class="modal-btn ${danger ? "modal-btn-danger" : "modal-btn-primary"}" id="modal-confirm" type="button">${esc(confirmLabel)}</button>
        </div>
      </div>
    </div>
  `;
}

/**
 * Project create/edit form body. Pre-fills name when editing.
 */
export function projectFormBody(project) {
  return `
    <label class="modal-field">
      <span>Name</span>
      <input id="field-name" type="text" maxlength="100" autocomplete="off" value="${esc(project ? project.name : "")}" />
    </label>
  `;
}

export function confirmBody(text) {
  return `<p class="modal-text">${esc(text)}</p>`;
}
