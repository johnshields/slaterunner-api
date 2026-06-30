import { RESOURCES } from "../config.js";

/**
 * OpenAPI -> form fields
 * Translates a Create model from the API's OpenAPI document into the field
 * descriptors the form registry (fields.js) consumes. Keeping the backend
 * schema as the single source means forms never drift from the Pydantic models.
 */

const UPPER = new Set(["uid", "id", "fps"]);

/**
 * Foreign-key fields: a property whose name is a resource's uid parameter
 * (e.g. project_uid) becomes a select populated from that resource.
 */
const REF_RESOURCE = Object.fromEntries(
  RESOURCES.filter((r) => r.uidParam).map((r) => [r.uidParam, r.key])
);

function humanize(key) {
  return key
    .split("_")
    .map((w) => (UPPER.has(w) ? w.toUpperCase() : w.charAt(0).toUpperCase() + w.slice(1)))
    .join(" ");
}

function deref(ref, schemas) {
  return schemas[ref.split("/").pop()] || {};
}

/**
 * Reduce a property schema to its concrete type, unwrapping $ref, allOf and the
 * anyOf[type, null] that Pydantic emits for Optional fields.
 */
function resolve(prop, schemas) {
  if (!prop) return {};
  if (prop.$ref) return resolve(deref(prop.$ref, schemas), schemas);
  if (prop.allOf) return resolve(prop.allOf[0], schemas);
  if (prop.anyOf) {
    const real = prop.anyOf.find((s) => s.type !== "null");
    return resolve(real, schemas);
  }
  return prop;
}

function fieldType(resolved) {
  if (resolved.enum) return "select";
  if (resolved.type === "integer" || resolved.type === "number") return "number";
  if (resolved.type === "object" || resolved.type === "array") return "json";
  return "text";
}

/**
 * Build field descriptors for a model. Skips the auto-generated uid.
 */
export function fieldsFromSchema(openapi, modelName) {
  const schemas = openapi.components.schemas;
  const model = schemas[modelName];
  const required = new Set(model.required || []);

  return Object.entries(model.properties)
    .filter(([key]) => key !== "uid")
    .map(([key, prop]) => {
      const resolved = resolve(prop, schemas);
      const field = {
        key,
        label: humanize(key),
        type: fieldType(resolved),
        required: required.has(key),
      };
      if (resolved.enum) field.options = resolved.enum;
      // Foreign key -> select populated from the referenced resource (filled in formDef)
      if (!resolved.enum && REF_RESOURCE[key]) {
        field.type = "select";
        field.ref = REF_RESOURCE[key];
      }
      if (prop.default !== undefined && prop.default !== null) field.default = prop.default;
      return field;
    });
}
