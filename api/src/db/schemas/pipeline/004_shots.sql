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
