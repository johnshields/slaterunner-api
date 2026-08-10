CREATE TABLE IF NOT EXISTS publishes (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    uid            TEXT UNIQUE,
    project_uid    TEXT NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    version_uid    TEXT NOT NULL REFERENCES versions (uid) ON DELETE CASCADE,
    type           TEXT NOT NULL,
    representation TEXT,
    path           TEXT NOT NULL,
    metadata       TEXT NOT NULL DEFAULT '{}',
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at     TEXT
);
