from fastapi import HTTPException
from clients.db import db


def db_lookup(table: str, identifier: str, *, name_column: str | None = "name") -> dict:
    """Lookup a record by UID, falling back to name column if provided."""
    result = db.table(table).select().eq("uid", identifier).limit(1).execute()

    if not result.data and name_column:
        result = db.table(table).select().eq(name_column, identifier).limit(1).execute()

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail=f"Record with UID or name '{identifier}' not found in '{table}'."
        )
    return result.data[0]
