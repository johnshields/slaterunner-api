import os
import secrets

from api.dependencies.auth import hash_token
from app.config import ROOT_DIR, settings
from db import db

DEV_TOKEN_FILE = os.path.join(ROOT_DIR, ".dev_token")
DEV_KEY_UID = "KEY_DEV"
BOOT_KEY_UID = "KEY_BOOT"


def _upsert_key(uid, hashed, description):
    """Keep a single fixed-uid admin key row matching the given token hash."""
    existing = db.table("api_keys").select("uid,token").eq("uid", uid).limit(1).execute()
    if existing.data:
        if existing.data[0]["token"] != hashed:
            db.table("api_keys").update({"token": hashed}).eq("uid", uid).execute()
    else:
        db.table("api_keys").insert({
            "uid": uid,
            "token": hashed,
            "description": description,
            "role": "admin",
            "is_admin": 1,
            "expires_at": None,
        }).execute()


def ensure_boot_token(logger):
    """
    Install the BOOT_TOKEN deployment secret as an admin key when provided.
    Runs in any environment so a fresh container is immediately usable.
    The raw token is never logged.
    """
    if not settings.BOOT_TOKEN:
        return
    _upsert_key(BOOT_KEY_UID, hash_token(settings.BOOT_TOKEN), "boot token")
    logger.info("boot admin token installed")


def ensure_dev_token(logger):
    """
    Development convenience: guarantee a usable admin token on boot.

    Persists the raw token to .dev_token (gitignored) so it stays stable across
    restarts, and upserts a single fixed-uid key row so it survives a reseed or
    a regenerated token file. Logs the raw token for pasting into the console.
    Never runs outside development.
    """
    if not settings.is_development():
        return

    raw = None
    if os.path.exists(DEV_TOKEN_FILE):
        with open(DEV_TOKEN_FILE) as fh:
            raw = fh.read().strip() or None

    if not raw:
        raw = secrets.token_urlsafe(32)
        with open(DEV_TOKEN_FILE, "w") as fh:
            fh.write(raw + "\n")

    _upsert_key(DEV_KEY_UID, hash_token(raw), "dev boot token")
    logger.info("dev admin token ready (paste into the console): %s", raw)
