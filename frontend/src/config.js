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
  { key: "projects", label: "Projects" },
  { key: "assets", label: "Assets" },
  { key: "shots", label: "Shots" },
  { key: "tasks", label: "Tasks" },
  { key: "versions", label: "Versions" },
  { key: "publishes", label: "Publishes" },
  { key: "renders", label: "Renders" },
  { key: "events", label: "Events" },
];
