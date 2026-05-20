from fastapi import HTTPException
from typing import Optional
from clients.db import db
from schemas.pipeline.shot import ShotCreate, ShotUpdate, ShotOut
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid


# Create a new shot, generate a UID if not provided.
def create_shot(data: ShotCreate) -> ShotOut:
    db_lookup("projects", data.project_uid)

    existing = (
        db.table("shots")
        .select("uid")
        .eq("project_uid", data.project_uid)
        .eq("seq", data.seq)
        .eq("shot", data.shot)
        .is_("deleted_at", "null")
        .limit(1)
        .execute()
    )
    if existing.data:
        raise HTTPException(
            status_code=409,
            detail=f"Shot '{data.seq}/{data.shot}' already exists in project '{data.project_uid}'.",
        )

    row = data.model_dump(exclude_none=True)
    row["uid"] = row.get("uid") or generate_uid("SHT")

    result = db.table("shots").insert(row).execute()
    return create_response(result.data[0], "Shot created successfully")


# Update a shot by UID
def update_shot(uid: str, data: ShotUpdate) -> ShotOut:
    shot = db_lookup("shots", uid, name_column=None)
    updates = data.model_dump(exclude_none=True)

    if "project_uid" in updates:
        db_lookup("projects", updates["project_uid"])

    if not updates:
        return create_response(shot, "Shot updated successfully")

    result = db.table("shots").update(updates).eq("uid", shot["uid"]).execute()
    return create_response(result.data[0], "Shot updated successfully")


# Delete a shot by UID (soft delete)
def delete_shot(uid: str) -> dict:
    db_lookup("shots", uid, name_column=None)
    db.table("shots").update({"deleted_at": "now()"}).eq("uid", uid).execute()
    return create_response(None, f"Shot '{uid}' deleted successfully")


# Get a list of shots, with optional filtering (excluding soft-deleted)
def list_shots(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        shot: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    query = db.table("shots").select("*", count="exact")

    if not include_deleted:
        query = query.is_("deleted_at", "null")
    if uid:
        query = query.eq("uid", uid)
    if project_uid:
        query = query.eq("project_uid", project_uid)
    if shot:
        query = query.ilike("shot", f"%{shot}%")

    result = query.order("shot").range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Shots retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }
