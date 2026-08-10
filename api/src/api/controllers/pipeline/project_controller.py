
from fastapi import HTTPException

from clients.db import db
from schemas.pipeline.project import (
    ProjectCreate,
    ProjectOut,
    ProjectOverviewOut,
    ProjectUpdate,
)
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid


# Create a new project, generate a UID if not provided
def create_project(data: ProjectCreate) -> ProjectOut:
    existing = (
        db.table("projects")
        .select("uid")
        .eq("name", data.name)
        .is_("deleted_at", "null")
        .limit(1)
        .execute()
    )
    if existing.data:
        raise HTTPException(status_code=409, detail=f"Project '{data.name}' already exists.")

    row = data.model_dump(exclude_none=True)
    row["uid"] = row.get("uid") or generate_uid("PRJ")

    result = db.table("projects").insert(row).execute()
    return create_response(result.data[0], "Project created successfully")


# Update a project by UID or name
def update_project(identifier: str, data: ProjectUpdate) -> ProjectOut:
    project = db_lookup("projects", identifier)
    updates = data.model_dump(exclude_none=True)

    if not updates:
        return create_response(project, "Project updated successfully")

    result = db.table("projects").update(updates).eq("uid", project["uid"]).execute()
    return create_response(result.data[0], "Project updated successfully")


# Delete a project by UID or name (soft delete)
def delete_project(identifier: str) -> dict:
    project = db_lookup("projects", identifier)
    db.table("projects").update({"deleted_at": "now()"}).eq("uid", project["uid"]).execute()
    return create_response(None, f"Project '{identifier}' deleted successfully")


# Get a list of all projects, with optional filtering (excluding soft-deleted)
def list_projects(
        uid: str | None = None,
        name: str | None = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    query = db.table("projects").select("*", count="exact")

    if not include_deleted:
        query = query.is_("deleted_at", "null")
    if uid:
        query = query.eq("uid", uid)
    if name:
        query = query.ilike("name", f"%{name}%")

    result = query.order("name").range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Projects retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }


# Get basic counts and info for a single project
def list_project_overview(project_uid: str) -> ProjectOverviewOut:
    project = db_lookup("projects", project_uid)

    shots_count = db.table("shots").select("*", count="exact").eq("project_uid", project_uid).limit(0).execute()
    tasks_count = (
        db.table("tasks")
        .select("*", count="exact")
        .eq("project_uid", project_uid)
        .eq("parent_type", "shot")
        .limit(0)
        .execute()
    )

    overview = ProjectOverviewOut(
        uid=project["uid"],
        name=project["name"],
        counts={"shots": shots_count.count or 0, "tasks": tasks_count.count or 0},
        created_at=project["created_at"],
    )
    return create_response(overview, "Project overview retrieved successfully")


# Get all assets belonging to a project
def list_project_assets(project_uid: str, limit: int = 50, offset: int = 0):
    db_lookup("projects", project_uid)

    result = (
        db.table("assets")
        .select("*", count="exact")
        .eq("project_uid", project_uid)
        .order("name")
        .range(offset, offset + limit - 1)
        .execute()
    )

    return {
        "status": "success",
        "message": "Project assets retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }


# Get all shots in a project, with optional filtering
def list_project_shots(
        project_uid: str,
        seq: str | None = None,
        shot: str | None = None,
        range: str | None = None,
        limit: int = 50,
        offset: int = 0,
):
    db_lookup("projects", project_uid)

    query = db.table("shots").select("*", count="exact").eq("project_uid", project_uid)

    if seq:
        query = query.eq("seq", seq)
    if shot:
        query = query.eq("shot", shot)
    if range:
        try:
            start, end = map(int, range.split("-"))
            query = query.gte("frame_in", start).lte("frame_out", end)
        except ValueError:
            raise ValueError("Invalid range format. Use start-end (e.g. 100-200).")

    result = query.order("seq").order("shot").range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Project shots retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }


# Get all tasks for a project, with optional filters
def list_project_tasks(
        project_uid: str,
        parent_type: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
):
    db_lookup("projects", project_uid)

    query = db.table("tasks").select("*", count="exact").eq("project_uid", project_uid)

    if parent_type:
        query = query.eq("parent_type", parent_type)
    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Project tasks retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }


# Get all publishes for a project, optionally filtered
def list_project_publishes(
        project_uid: str,
        type: str | None = None,
        rep: str | None = None,
        limit: int = 50,
        offset: int = 0,
):
    db_lookup("projects", project_uid)

    query = db.table("publishes").select("*", count="exact").eq("project_uid", project_uid)

    if type:
        query = query.eq("type", type)
    if rep:
        query = query.eq("representation", rep)

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Project publishes retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }
