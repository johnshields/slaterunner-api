from datetime import UTC, datetime


def now_utc() -> datetime:
    """Get current UTC timestamp for consistent datetime handling."""
    return datetime.now(UTC)

