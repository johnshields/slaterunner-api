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
