DROP TABLE IF EXISTS projects CASCADE;

CREATE TABLE projects (
    id         SERIAL PRIMARY KEY,
    uid        TEXT UNIQUE          DEFAULT gen_uid('PRJ'),
    name       TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TRIGGER trg_projects_updated
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
