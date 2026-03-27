CREATE TABLE tasks (
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE          DEFAULT gen_uid('TASK'),
    project_uid TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    parent_type TEXT        NOT NULL CHECK (parent_type IN ('asset', 'shot')),
    parent_uid  TEXT        NOT NULL,
    name        TEXT        NOT NULL,
    assignee    TEXT,
    status      TEXT        NOT NULL DEFAULT 'WIP' CHECK (status IN ('WIP', 'READY', 'HOLD', 'DONE')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TRIGGER trg_tasks_updated
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
