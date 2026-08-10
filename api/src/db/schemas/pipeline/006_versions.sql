CREATE TABLE IF NOT EXISTS versions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    uid         TEXT UNIQUE,
    project_uid TEXT    NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    task_uid    TEXT    NOT NULL REFERENCES tasks (uid) ON DELETE CASCADE,
    vnum        INTEGER NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'draft' CHECK (
        status IN ('draft', 'review', 'approved', 'rejected')
    ),
    created_by  TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at  TEXT,
    UNIQUE (task_uid, vnum)
);
