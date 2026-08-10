CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    uid         TEXT UNIQUE,
    project_uid TEXT NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    parent_type TEXT NOT NULL CHECK (parent_type IN ('asset', 'shot')),
    parent_uid  TEXT NOT NULL,
    name        TEXT NOT NULL,
    assignee    TEXT,
    status      TEXT NOT NULL DEFAULT 'WIP' CHECK (status IN ('WIP', 'READY', 'HOLD', 'DONE')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at  TEXT
);
