
from fastapi import HTTPException

from db import db
from schemas.pipeline.asset import AssetCreate, AssetOut, AssetUpdate
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid


# Create a new asset, generate a UID if not provided.
def create_asset(data: AssetCreate) -> AssetOut:
    db_lookup("projects", data.project_uid)

    existing = (
        db.table("assets")
        .select("uid")
        .eq("project_uid", data.project_uid)
        .eq("name", data.name)
        .is_("deleted_at", "null")
        .limit(1)
        .execute()
    )
    if existing.data:
        raise HTTPException(
            status_code=409,
            detail=f"Asset '{data.name}' already exists in project '{data.project_uid}'.",
        )

    row = data.model_dump(exclude_none=True)
    row["uid"] = row.get("uid") or generate_uid("AST")

    result = db.table("assets").insert(row).execute()
    return create_response(result.data[0], "Asset created successfully")


# Update an asset by UID or name
def update_asset(identifier: str, data: AssetUpdate) -> AssetOut:
    asset = db_lookup("assets", identifier)
    updates = data.model_dump(exclude_none=True)

    if "project_uid" in updates:
        db_lookup("projects", updates["project_uid"])

    if not updates:
        return create_response(asset, "Asset updated successfully")

    result = db.table("assets").update(updates).eq("uid", asset["uid"]).execute()
    return create_response(result.data[0], "Asset updated successfully")


# Delete an asset by UID or name (soft delete)
def delete_asset(identifier: str) -> dict:
    asset = db_lookup("assets", identifier)
    db.table("assets").update({"deleted_at": "now()"}).eq("uid", asset["uid"]).execute()
    return create_response(None, f"Asset '{identifier}' deleted successfully")


# Get a list of all assets, with optional filtering (excluding soft-deleted)
def list_assets(
        uid: str | None = None,
        project_uid: str | None = None,
        name: str | None = None,
        type: str | None = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    query = db.table("assets").select("*", count="exact")

    if not include_deleted:
        query = query.is_("deleted_at", "null")
    if uid:
        query = query.eq("uid", uid)
    if project_uid:
        query = query.eq("project_uid", project_uid)
    if name:
        query = query.ilike("name", f"%{name}%")
    if type:
        query = query.eq("type", type)

    result = query.order("name").range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Assets retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }


# Get all tasks belonging to an asset
def list_asset_tasks(asset_uid: str, limit: int = 50, offset: int = 0):
    db_lookup("assets", asset_uid)

    result = (
        db.table("tasks")
        .select("*", count="exact")
        .eq("parent_type", "asset")
        .eq("parent_uid", asset_uid)
        .order("name")
        .range(offset, offset + limit - 1)
        .execute()
    )

    return {
        "status": "success",
        "message": "Asset tasks retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }
