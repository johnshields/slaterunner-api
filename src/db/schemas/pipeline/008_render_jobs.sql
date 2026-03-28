DROP TABLE IF EXISTS render_jobs CASCADE;

CREATE TABLE render_jobs (
    id           SERIAL PRIMARY KEY,
    uid          TEXT UNIQUE          DEFAULT gen_uid('RJB'),
    project_uid  TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    version_uid  TEXT        REFERENCES versions (uid) ON DELETE SET NULL,
    context      JSONB       NOT NULL,
    adapter      TEXT        NOT NULL,
    status       TEXT        NOT NULL DEFAULT 'queued' CHECK (
        status IN ('queued', 'running', 'succeeded', 'failed')
    ),
    logs         TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at   TIMESTAMPTZ
);

CREATE TRIGGER trg_render_jobs_updated
    BEFORE UPDATE ON render_jobs
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
