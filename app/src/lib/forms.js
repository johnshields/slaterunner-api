import { api } from "./api.js";
import { primaryLabel } from "./records.js";
import { fieldsFromSchema } from "../ui/schema-fields.js";

/**
 * Resource write config
 * The only hand-maintained mapping: a resource's singular noun and the name of
 * its Create model in the OpenAPI document. Field definitions are derived from
 * that schema (see ui/schema-fields.js), so they stay in sync with the backend.
 */
export const RESOURCE_MODELS = {
  projects: { noun: "project", model: "ProjectCreate" },
  assets: { noun: "asset", model: "AssetCreate" },
  shots: { noun: "shot", model: "ShotCreate" },
  tasks: { noun: "task", model: "TaskCreate" },
  versions: { noun: "version", model: "VersionCreate" },
  publishes: { noun: "publish", model: "PublishCreate" },
  renders: { noun: "render", model: "RenderJobCreate" },
  events: { noun: "event", model: "EventCreate" },
};

export const WRITABLE = new Set(Object.keys(RESOURCE_MODELS));

let relationshipCache = null;

/**
 * Map each resource to the children that hold a foreign key to it, so a parent
 * record can spawn a pre-filled child form. Derived from the schema ref fields.
 * Returns { [parentResource]: [{ resource, fkKey, noun }] }.
 */
export async function relationships() {
  if (relationshipCache) return relationshipCache;
  const openapi = await api.schema();
  const map = {};
  for (const [resource, { noun, model }] of Object.entries(RESOURCE_MODELS)) {
    for (const f of fieldsFromSchema(openapi, model)) {
      if (f.ref) (map[f.ref] ||= []).push({ resource, fkKey: f.key, noun });
    }
  }
  relationshipCache = map;
  return map;
}

/**
 * Fetch a referenced resource's records as { value, label } select options.
 */
async function refOptions(resource) {
  const res = await api.list(resource, 500, 0);
  if (!res.ok) return [];
  const json = await res.json().catch(() => ({}));
  return (json.data || []).map((r) => {
    const label = primaryLabel(r);
    return { value: r.uid, label: label === r.uid ? r.uid : `${label} (${r.uid})` };
  });
}

/**
 * Build a form definition for a resource from the live OpenAPI schema,
 * resolving foreign-key fields to dropdown options.
 */
export async function formDef(resource) {
  const { noun, model } = RESOURCE_MODELS[resource];
  const openapi = await api.schema();
  const fields = fieldsFromSchema(openapi, model);
  await Promise.all(
    fields
      .filter((f) => f.ref)
      .map(async (f) => {
        f.options = await refOptions(f.ref);
      })
  );
  return { noun, fields };
}
