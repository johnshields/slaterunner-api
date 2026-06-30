-- API Keys: table, RPC functions, RLS, and seed data

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

-- RPC: get all API keys (admin/service only)
CREATE OR REPLACE FUNCTION get_all_api_keys(p_token TEXT DEFAULT NULL)
RETURNS TABLE (
  id INTEGER,
  uid TEXT,
  description TEXT,
  role TEXT,
  is_admin BOOLEAN,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
) AS $$
BEGIN
  IF p_token IS NOT NULL THEN
    PERFORM set_config('app.current_token', p_token, true);
    IF NOT (is_admin() OR is_service()) THEN
      RAISE EXCEPTION 'Access denied: requires admin or service role';
    END IF;
  END IF;

  RETURN QUERY
    SELECT k.id, k.uid, k.description, k.role, k.is_admin, k.expires_at, k.created_at, k.updated_at
    FROM api_keys k
    ORDER BY k.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RPC: create API key (admin/service only, returns unhashed token once)
CREATE OR REPLACE FUNCTION create_api_key(
  p_token TEXT DEFAULT NULL,
  p_description TEXT DEFAULT NULL,
  p_role TEXT DEFAULT NULL,
  p_is_admin BOOLEAN DEFAULT false,
  p_expires_at TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
  uid TEXT,
  original_token TEXT,
  description TEXT,
  role TEXT,
  is_admin BOOLEAN,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ
) AS $$
DECLARE
  v_new_token TEXT;
  v_uid TEXT;
  v_created_at TIMESTAMPTZ;
  v_is_admin BOOLEAN;
BEGIN
  IF p_token IS NOT NULL THEN
    PERFORM set_config('app.current_token', p_token, true);
    IF NOT (is_admin() OR is_service()) THEN
      RAISE EXCEPTION 'Access denied: requires admin or service role';
    END IF;
  END IF;

  IF p_role NOT IN ('admin', 'td', 'atd', 'artist', 'producer', 'supervisor', 'service', 'system', 'client') THEN
    RAISE EXCEPTION 'Invalid role: %', p_role;
  END IF;

  v_is_admin := (p_role = 'admin');
  v_new_token := gen_token();

  INSERT INTO api_keys (token, description, role, is_admin, expires_at)
  VALUES (hash_token(v_new_token), p_description, p_role, v_is_admin, p_expires_at)
  RETURNING api_keys.uid, api_keys.created_at INTO v_uid, v_created_at;

  RETURN QUERY SELECT v_uid, v_new_token, p_description, p_role, v_is_admin, p_expires_at, v_created_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RPC: expire API key (admin/service only)
CREATE OR REPLACE FUNCTION expire_api_key(p_token TEXT DEFAULT NULL, p_uid TEXT DEFAULT NULL)
RETURNS TABLE (
  uid TEXT,
  description TEXT,
  role TEXT,
  expires_at TIMESTAMPTZ
) AS $$
DECLARE
  v_result RECORD;
BEGIN
  IF p_token IS NOT NULL THEN
    PERFORM set_config('app.current_token', p_token, true);
    IF NOT (is_admin() OR is_service()) THEN
      RAISE EXCEPTION 'Access denied: requires admin or service role';
    END IF;
  END IF;

  UPDATE api_keys k
  SET expires_at = now()
  WHERE k.uid = p_uid
  RETURNING k.uid, k.description, k.role, k.expires_at INTO v_result;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'API key not found: %', p_uid;
  END IF;

  RETURN QUERY SELECT v_result.uid, v_result.description, v_result.role, v_result.expires_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Seed API keys (hashed, originals displayed via temp table)
CREATE TEMP TABLE api_tokens_temp (
  role TEXT,
  original_token TEXT,
  uid TEXT
);

DO $$
DECLARE
  admin_token TEXT;
  td_token TEXT;
  service_token TEXT;
  admin_uid TEXT;
  td_uid TEXT;
  service_uid TEXT;
BEGIN
  admin_token := gen_token();
  td_token := gen_token();
  service_token := gen_token();

  INSERT INTO api_keys (token, description, role, is_admin, expires_at)
  VALUES (hash_token(admin_token), 'Admin (full access)', 'admin', true, NULL)
  RETURNING uid INTO admin_uid;

  INSERT INTO api_keys (token, description, role, is_admin, expires_at)
  VALUES (hash_token(td_token), 'TD (pipeline full access)', 'td', true, NULL)
  RETURNING uid INTO td_uid;

  INSERT INTO api_keys (token, description, role, is_admin, expires_at)
  VALUES (hash_token(service_token), 'Service (render/events/logging)', 'service', false, NULL)
  RETURNING uid INTO service_uid;

  INSERT INTO api_tokens_temp (role, original_token, uid) VALUES
  ('admin', admin_token, admin_uid),
  ('td', td_token, td_uid),
  ('service', service_token, service_uid);
END $$;

SELECT role, original_token, uid FROM api_tokens_temp ORDER BY role;

-- Row Level Security
ALTER TABLE api_keys DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS api_keys_admin_service_policy ON api_keys;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys FORCE ROW LEVEL SECURITY;

CREATE POLICY api_keys_admin_service_policy
  ON api_keys FOR ALL
  USING (is_admin() OR is_service())
  WITH CHECK (is_admin() OR is_service());
