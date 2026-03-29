-- Required for gen_random_bytes() and digest()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Helper: UID generator (PREFIX_XXXXXX)
CREATE OR REPLACE FUNCTION gen_uid(prefix TEXT) RETURNS TEXT AS $$
BEGIN
  RETURN prefix || '_' || upper(substr(encode(gen_random_bytes(4), 'hex'), 1, 6));
END;
$$ LANGUAGE plpgsql;

-- Helper: keep updated_at fresh
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Helper: generate random API token (hex-encoded)
CREATE OR REPLACE FUNCTION gen_token(p_bytes INT DEFAULT 32) RETURNS TEXT AS $$
BEGIN
  RETURN encode(gen_random_bytes(p_bytes), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Helper: hash token with SHA256
CREATE OR REPLACE FUNCTION hash_token(token_value TEXT) RETURNS TEXT AS $$
BEGIN
  RETURN encode(digest(token_value, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Helper: check if current session token is valid
CREATE OR REPLACE FUNCTION is_valid_api_token() RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM api_keys k
    WHERE k.token = hash_token(current_setting('app.current_token', true))
      AND (k.expires_at IS NULL OR k.expires_at > now())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper: check if current session token has a specific role
CREATE OR REPLACE FUNCTION has_role(target_role TEXT) RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM api_keys k
    WHERE k.token = hash_token(current_setting('app.current_token', true))
      AND k.role = target_role
      AND (k.expires_at IS NULL OR k.expires_at > now())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper: check if current token is admin
CREATE OR REPLACE FUNCTION is_admin() RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM api_keys k
    WHERE k.token = hash_token(current_setting('app.current_token', true))
      AND (k.is_admin = true OR k.role = 'admin')
      AND (k.expires_at IS NULL OR k.expires_at > now())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper: check if current token is service role
CREATE OR REPLACE FUNCTION is_service() RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM api_keys k
    WHERE k.token = hash_token(current_setting('app.current_token', true))
      AND k.role = 'service'
      AND (k.expires_at IS NULL OR k.expires_at > now())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper: validate an API token (bypasses RLS for auth)
CREATE OR REPLACE FUNCTION validate_api_token(token_value TEXT)
RETURNS TABLE(valid BOOLEAN, role TEXT, is_admin BOOLEAN, expires_at TIMESTAMPTZ) AS $$
BEGIN
  RETURN QUERY
  SELECT
    CASE WHEN k.expires_at IS NULL OR k.expires_at > now() THEN true ELSE false END AS valid,
    k.role,
    k.is_admin,
    k.expires_at
  FROM api_keys k
  WHERE k.token = hash_token(token_value);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
