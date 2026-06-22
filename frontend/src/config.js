/**
 * Frontend configuration
 */

export const TOKEN_KEY = "sr_token";
export const PAGE_SIZE = 50;

/**
 * Resources
 * "status" is a synthetic view backed by the unauthenticated /api endpoint.
 * The rest map 1:1 to GET /api/v1/{key} (Bearer auth, paginated).
 */
export const RESOURCES = [
  { key: "status", label: "Status", synthetic: true },
  { key: "projects", label: "Projects", uidParam: "project_uid" },
  { key: "assets", label: "Assets", uidParam: "asset_uid" },
  { key: "shots", label: "Shots", uidParam: "shot_uid" },
  { key: "tasks", label: "Tasks", uidParam: "task_uid" },
  { key: "versions", label: "Versions", uidParam: "version_uid" },
  { key: "publishes", label: "Publishes", uidParam: "publish_uid" },
  { key: "renders", label: "Renders", uidParam: "render_uid" },
  { key: "events", label: "Events", uidParam: "event_uid" },
];
