from typing import Optional
from clients.db import db
from schemas.pipeline.publish import PublishOut, PublishCreate, PublishUpdate
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid


# Create a new publish
def create_publish(data: PublishCreate) -> PublishOut:
    db_lookup("projects", data.project_uid)
    db_lookup("versions", data.version_uid, name_column=None)

    row = data.model_dump(exclude_none=True)
    row["uid"] = row.get("uid") or generate_uid("PUB")
    # Schema uses "meta" but DB column is "metadata"
    if "meta" in row:
        row["metadata"] = row.pop("meta")

    result = db.table("publishes").insert(row).execute()
    return create_response(result.data[0], "Publish created successfully")


# Update a publish by UID
def update_publish(uid: str, data: PublishUpdate) -> PublishOut:
    publish = db_lookup("publishes", uid, name_column=None)
    updates = data.model_dump(exclude_none=True)

    # Schema uses "meta" but DB column is "metadata"
    if "meta" in updates:
        updates["metadata"] = updates.pop("meta")

    if not updates:
        return create_response(publish, "Publish updated successfully")

    result = db.table("publishes").update(updates).eq("uid", publish["uid"]).execute()
    return create_response(result.data[0], "Publish updated successfully")


# Delete a publish by UID (soft delete)
def delete_publish(uid: str) -> dict:
    db_lookup("publishes", uid, name_column=None)
    db.table("publishes").update({"deleted_at": "now()"}).eq("uid", uid).execute()
    return create_response(None, f"Publish '{uid}' deleted successfully")


# Get a list of all publishes, with optional filtering (excluding soft-deleted)
def list_publishes(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        version_uid: Optional[str] = None,
        type: Optional[str] = None,
        representation: Optional[str] = None,
        path: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    query = db.table("publishes").select("*", count="exact")

    if not include_deleted:
        query = query.is_("deleted_at", "null")
    if uid:
        query = query.eq("uid", uid)
    if project_uid:
        query = query.eq("project_uid", project_uid)
    if version_uid:
        query = query.eq("version_uid", version_uid)
    if type:
        query = query.eq("type", type)
    if representation:
        query = query.eq("representation", representation)
    if path:
        query = query.ilike("path", f"%{path}%")

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Publishes retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }
