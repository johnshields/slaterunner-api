import os
import secrets

from app.config import settings, ROOT_DIR
from clients.db import db
from api.dependencies.auth import hash_token

DEV_TOKEN_FILE = os.path.join(ROOT_DIR, ".dev_token")
DEV_KEY_UID = "KEY_DEV"


def ensure_dev_token(logger):
    """
    Development convenience: guarantee a usable admin token on boot.

    Persists the raw token to .dev_token (gitignored) so it stays stable across
    restarts, and upserts a single fixed-uid key row so it survives a reseed or
    a regenerated token file. Logs the raw token for pasting into the console.
    Never runs outside development.
    """
    if not settings.is_development:
        return

    raw = None
    if os.path.exists(DEV_TOKEN_FILE):
        with open(DEV_TOKEN_FILE) as fh:
            raw = fh.read().strip() or None

    if not raw:
        raw = secrets.token_urlsafe(32)
        with open(DEV_TOKEN_FILE, "w") as fh:
            fh.write(raw + "\n")

    hashed = hash_token(raw)
    existing = db.table("api_keys").select("uid,token").eq("uid", DEV_KEY_UID).limit(1).execute()
    if existing.data:
        if existing.data[0]["token"] != hashed:
            db.table("api_keys").update({"token": hashed}).eq("uid", DEV_KEY_UID).execute()
    else:
        db.table("api_keys").insert({
            "uid": DEV_KEY_UID,
            "token": hashed,
            "description": "dev boot token",
            "role": "admin",
            "is_admin": 1,
            "expires_at": None,
        }).execute()

    logger.info("dev admin token ready (paste into the console): %s", raw)
