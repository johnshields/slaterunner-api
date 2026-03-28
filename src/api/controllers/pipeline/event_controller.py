from typing import Optional
from clients.supabase import supabase
from schemas.pipeline.event import EventOut, EventCreate, EventUpdate
from schemas.response import create_response
from utils.database import sb_lookup
from utils.uid import generate_uid


# Get a list of events with optional filtering (excluding soft-deleted)
def list_events(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        kind: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    query = supabase.table("events").select("*", count="exact")

    if not include_deleted:
        query = query.is_("deleted_at", "null")
    if uid:
        query = query.eq("uid", uid)
    if project_uid:
        query = query.eq("project_uid", project_uid)
    if kind:
        query = query.eq("kind", kind)

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Events retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }


# Create a new event
def create_event(data: EventCreate) -> EventOut:
    sb_lookup("projects", data.project_uid)

    row = data.model_dump(exclude_none=True)
    row["uid"] = row.get("uid") or generate_uid("EVN")

    result = supabase.table("events").insert(row).execute()
    return create_response(result.data[0], "Event created successfully")


# Update an event by UID
def update_event(uid: str, data: EventUpdate) -> EventOut:
    event = sb_lookup("events", uid, name_column=None)
    updates = data.model_dump(exclude_none=True)

    if not updates:
        return create_response(event, "Event updated successfully")

    result = supabase.table("events").update(updates).eq("uid", event["uid"]).execute()
    return create_response(result.data[0], "Event updated successfully")


# Delete an event by UID (soft delete)
def delete_event(uid: str) -> dict:
    sb_lookup("events", uid, name_column=None)
    supabase.table("events").update({"deleted_at": "now()"}).eq("uid", uid).execute()
    return create_response(None, f"Event '{uid}' deleted successfully")
