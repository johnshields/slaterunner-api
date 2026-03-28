DROP TABLE IF EXISTS shots CASCADE;

CREATE TABLE shots (
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE            DEFAULT gen_uid('SHT'),
    project_uid TEXT          NOT NULL REFERENCES projects (uid) ON DELETE CASCADE,
    seq         TEXT          NOT NULL,
    shot        TEXT          NOT NULL,
    frame_in    INT           NOT NULL,
    frame_out   INT           NOT NULL,
    fps         NUMERIC(6, 3) NOT NULL DEFAULT 24.0,
    colorspace  TEXT          NOT NULL DEFAULT 'sRGB',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TRIGGER trg_shots_updated
    BEFORE UPDATE ON shots
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
