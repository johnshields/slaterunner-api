from datetime import UTC, datetime

from fastapi import FastAPI

from app.config import settings
from db import db


def status_payload(app: FastAPI) -> dict:
    now = datetime.now(UTC)
    started = getattr(app.state, "started_at", now)
    uptime_seconds = (now - started).total_seconds()

    return {
        "ok": True,
        "service": app.title,
        "version": app.version,
        "api_version": settings.API_VERSION,
        "uptime_seconds": int(uptime_seconds),
        "message": app.description,
        "timestamp": now.isoformat(),
    }


def db_conn() -> dict:
    try:
        db.ping()
        return {"ok": True, "db": "d1"}
    except Exception as e:
        return {"ok": False, "db": f"error: {e.__class__.__name__}"}
