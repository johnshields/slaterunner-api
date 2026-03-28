from fastapi import FastAPI
from datetime import datetime, timezone
from app.config import settings
from clients.supabase import supabase


def status_payload(app: FastAPI) -> dict:
    now = datetime.now(timezone.utc)
    started = getattr(app.state, "started_at", now)
    uptime_seconds = (now - started).total_seconds()

    return {
        "ok": True,
        "service": getattr(app, "title"),
        "version": getattr(app, "version"),
        "api_version": settings.API_VERSION,
        "uptime_seconds": int(uptime_seconds),
        "message": getattr(app, "description"),
        "timestamp": now.isoformat(),
    }


def db_conn() -> dict:
    try:
        supabase.table("api_keys").select("id").limit(1).execute()
        return {"ok": True, "db": "ready"}
    except Exception as e:
        return {"ok": False, "db": f"error: {e.__class__.__name__}"}
