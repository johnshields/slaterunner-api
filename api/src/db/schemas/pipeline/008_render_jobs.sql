CREATE TABLE IF NOT EXISTS render_jobs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    uid          TEXT UNIQUE,
    project_uid  TEXT NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    version_uid  TEXT REFERENCES versions (uid) ON DELETE SET NULL,
    context      TEXT NOT NULL,
    adapter      TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'queued' CHECK (
        status IN ('queued', 'running', 'succeeded', 'failed')
    ),
    logs         TEXT,
    submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at   TEXT
);
