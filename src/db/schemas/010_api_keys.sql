DROP TABLE IF EXISTS api_keys CASCADE;

CREATE TABLE api_keys (
    id          SERIAL PRIMARY KEY,
    uid         TEXT UNIQUE DEFAULT gen_uid('APK'),
    token       TEXT UNIQUE NOT NULL,
    description TEXT,
    role        TEXT NOT NULL CHECK (role IN (
        'admin', 'td', 'atd', 'artist', 'producer', 'supervisor',
        'service', 'system', 'client'
    )),
    is_admin    BOOLEAN NOT NULL DEFAULT false,
    expires_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_api_keys_updated
    BEFORE UPDATE ON api_keys
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Helper: check if the current session token is valid
CREATE OR REPLACE FUNCTION is_valid_api_token() RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM api_keys k
    WHERE k.token = current_setting('app.current_token', true)
      AND (k.expires_at IS NULL OR k.expires_at > now())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper: check if the current session token has a specific role
CREATE OR REPLACE FUNCTION has_role(target_role TEXT) RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM api_keys k
    WHERE k.token = current_setting('app.current_token', true)
      AND k.role = target_role
      AND (k.expires_at IS NULL OR k.expires_at > now())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
