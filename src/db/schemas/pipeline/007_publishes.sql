CREATE TABLE publishes (
    id             SERIAL PRIMARY KEY,
    uid            TEXT UNIQUE          DEFAULT gen_uid('PUB'),
    project_uid    TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    version_uid    TEXT        NOT NULL REFERENCES versions (uid) ON DELETE CASCADE,
    type           TEXT        NOT NULL,
    representation TEXT,
    path           TEXT        NOT NULL,
    metadata       JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at     TIMESTAMPTZ
);

CREATE TRIGGER trg_publishes_updated
    BEFORE UPDATE ON publishes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
