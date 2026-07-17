import { renderFields, parseField } from "./fields.js";

/**
 * ResourceForm
 * Wraps a resource form definition ({ noun, fields }) with rendering and value
 * collection. Field rendering and coercion are delegated to the field-type
 * registry (fields.js); the server remains the source of truth for validation.
 */
export class ResourceForm {
  constructor(def) {
    this.def = def;
  }

  get noun() {
    return this.def.noun;
  }

  render(record) {
    return renderFields(this.def.fields, record);
  }

  /**
   * Read field values into a request body. Empty optionals are omitted; a
   * missing required field or invalid input throws a user-facing message.
   */
  collect() {
    const body = {};
    for (const f of this.def.fields) {
      const raw = document.querySelector(`#field-${f.key}`).value.trim();
      if (raw === "") {
        if (f.required) throw new Error(`${f.label} is required.`);
        continue;
      }
      body[f.key] = parseField(f, raw);
    }
    return body;
  }
}
