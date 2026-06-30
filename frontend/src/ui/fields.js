import { esc } from "../utils.js";

/**
 * Field types
 * Each type colocates its control markup with value parsing, so rendering and
 * collection cannot drift. Add a new field type by adding one entry here —
 * nothing else changes.
 */
const FIELD_TYPES = {
  text: {
    control: (f, v) => `<input id="field-${f.key}" type="text" value="${esc(v)}" autocomplete="off" />`,
    parse: (raw) => raw,
  },
  number: {
    control: (f, v) => `<input id="field-${f.key}" type="number" value="${esc(v)}" autocomplete="off" />`,
    parse: (raw) => Number(raw),
  },
  select: {
    control: (f, v) => {
      const options = ['<option value="">—</option>']
        .concat(
          (f.options || []).map((o) => {
            const value = typeof o === "object" ? o.value : o;
            const text = typeof o === "object" ? o.label : o;
            return `<option value="${esc(value)}"${String(v) === String(value) ? " selected" : ""}>${esc(text)}</option>`;
          })
        )
        .join("");
      return `<select id="field-${f.key}">${options}</select>`;
    },
    parse: (raw) => raw,
  },
  json: {
    control: (f, v) => {
      const text = v && typeof v === "object" ? JSON.stringify(v, null, 2) : "";
      return `<textarea id="field-${f.key}" rows="4" spellcheck="false">${esc(text)}</textarea>`;
    },
    parse: (raw, f) => {
      try {
        return JSON.parse(raw);
      } catch {
        throw new Error(`${f.label} must be valid JSON.`);
      }
    },
  },
};

function typeOf(field) {
  return FIELD_TYPES[field.type] || FIELD_TYPES.text;
}

function currentValue(field, record) {
  const v = record && record[field.key] != null ? record[field.key] : field.default;
  return v != null ? v : "";
}

/**
 * Render a form's fields, pre-filling from a record when editing.
 */
export function renderFields(fields, record) {
  const rows = fields
    .map(
      (f) => `
      <label class="modal-field">
        <span>${esc(f.label)}${f.required ? " *" : ""}</span>
        ${typeOf(f).control(f, currentValue(f, record))}
      </label>`
    )
    .join("");
  return `<div class="modal-form">${rows}</div>`;
}

/**
 * Coerce a non-empty raw field value by type. Throws on invalid JSON.
 * Empty/required handling lives in the form, so types only coerce real input.
 */
export function parseField(field, raw) {
  return typeOf(field).parse(raw, field);
}
