CREATE TABLE versions (
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE          DEFAULT gen_uid('VER'),
    project_uid TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    task_uid    TEXT        NOT NULL REFERENCES tasks (uid) ON DELETE CASCADE,
    vnum        INT         NOT NULL,
    status      TEXT        NOT NULL DEFAULT 'draft' CHECK (
        status IN ('draft', 'review', 'approved', 'rejected')
    ),
    created_by  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ,
    UNIQUE (task_uid, vnum)
);

CREATE TRIGGER trg_versions_updated
    BEFORE UPDATE ON versions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
