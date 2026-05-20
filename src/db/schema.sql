-- slaterunner SQLite schema

-- API keys
CREATE TABLE IF NOT EXISTS api_keys (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    uid         TEXT UNIQUE,
    token       TEXT UNIQUE NOT NULL,
    description TEXT,
    role        TEXT NOT NULL CHECK (role IN (
        'admin', 'td', 'atd', 'artist', 'producer', 'supervisor',
        'service', 'system', 'client'
    )),
    is_admin    INTEGER NOT NULL DEFAULT 0,
    expires_at  TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    uid        TEXT UNIQUE,
    name       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at TEXT
);

-- Assets
CREATE TABLE IF NOT EXISTS assets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    uid         TEXT UNIQUE,
    project_uid TEXT NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    type        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at  TEXT
);

-- Shots
CREATE TABLE IF NOT EXISTS shots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    uid         TEXT UNIQUE,
    project_uid TEXT    NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    seq         TEXT    NOT NULL,
    shot        TEXT    NOT NULL,
    frame_in    INTEGER NOT NULL,
    frame_out   INTEGER NOT NULL,
    fps         REAL    NOT NULL DEFAULT 24.0,
    colorspace  TEXT    NOT NULL DEFAULT 'sRGB',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    deleted_at  TEXT
);

-- Tasks
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

-- Versions
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

-- Publishes
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

-- Render jobs
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

-- Events
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    uid         TEXT UNIQUE,
    project_uid TEXT NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    kind        TEXT NOT NULL,
    payload     TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at  TEXT
);

-- Partial unique indexes (enforce uniqueness for non-deleted records only)
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_name_unique
    ON projects(name) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_assets_project_name_unique
    ON assets(project_uid, name) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_shots_project_seq_shot_unique
    ON shots(project_uid, seq, shot) WHERE deleted_at IS NULL;

-- Soft delete cascades
CREATE TRIGGER IF NOT EXISTS trg_cascade_soft_delete_project
    AFTER UPDATE OF deleted_at ON projects
    WHEN NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL
BEGIN
    UPDATE assets      SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE shots       SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE tasks       SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE versions    SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE publishes   SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE render_jobs SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE events      SET deleted_at = NEW.deleted_at WHERE project_uid = NEW.uid AND deleted_at IS NULL;
END;

CREATE TRIGGER IF NOT EXISTS trg_cascade_soft_delete_task
    AFTER UPDATE OF deleted_at ON tasks
    WHEN NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL
BEGIN
    UPDATE versions SET deleted_at = NEW.deleted_at WHERE task_uid = NEW.uid AND deleted_at IS NULL;
END;

CREATE TRIGGER IF NOT EXISTS trg_cascade_soft_delete_version
    AFTER UPDATE OF deleted_at ON versions
    WHEN NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL
BEGIN
    UPDATE publishes   SET deleted_at = NEW.deleted_at WHERE version_uid = NEW.uid AND deleted_at IS NULL;
    UPDATE render_jobs SET deleted_at = NEW.deleted_at WHERE version_uid = NEW.uid AND deleted_at IS NULL;
END;
