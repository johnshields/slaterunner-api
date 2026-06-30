import { api } from "./api.js";
import { fieldsFromSchema } from "./ui/schema-fields.js";

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

/**
 * Build a form definition for a resource from the live OpenAPI schema.
 */
export async function formDef(resource) {
  const { noun, model } = RESOURCE_MODELS[resource];
  const openapi = await api.schema();
  return { noun, fields: fieldsFromSchema(openapi, model) };
}
