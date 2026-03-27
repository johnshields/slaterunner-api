CREATE TABLE events (
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE          DEFAULT gen_uid('EVENT'),
    project_uid TEXT        NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    kind        TEXT        NOT NULL,
    payload     JSONB       NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TRIGGER trg_events_updated
    BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
