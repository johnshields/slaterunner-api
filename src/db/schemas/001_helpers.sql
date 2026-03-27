-- Required for gen_random_bytes()
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
