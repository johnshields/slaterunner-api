from datetime import datetime, timezone


def now_utc() -> datetime:
    """Get current UTC timestamp for consistent datetime handling."""
    return datetime.now(timezone.utc)

