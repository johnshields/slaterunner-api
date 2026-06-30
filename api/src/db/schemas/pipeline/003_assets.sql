DROP TABLE IF EXISTS assets CASCADE;

CREATE TABLE assets (
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE          DEFAULT gen_uid('AST'),
    project_uid TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    name        TEXT        NOT NULL,
    type        TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TRIGGER trg_assets_updated
    BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
