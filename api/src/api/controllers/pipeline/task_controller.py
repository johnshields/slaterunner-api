
from fastapi import HTTPException

from clients.db import db
from schemas.pipeline.task import TaskCreate, TaskOut, TaskUpdate
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid

TASK_DEFAULT_STATUS = "WIP"
VERSION_DEFAULT_STATUS = "draft"


# Create a new task, generate a UID if not provided, and auto-create Version v1.
def create_task(data: TaskCreate, *, created_by: str | None = None) -> TaskOut:
    db_lookup("projects", data.project_uid)

    row = data.model_dump(exclude_none=True)
    row["uid"] = row.get("uid") or generate_uid("TSK")
    row.setdefault("status", TASK_DEFAULT_STATUS)

    result = db.table("tasks").insert(row).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create task")

    task = result.data[0]

    # Auto-create initial version v1 with draft status
    ver_row = {
        "uid": generate_uid("VER"),
        "project_uid": task["project_uid"],
        "task_uid": task["uid"],
        "vnum": 1,
        "status": VERSION_DEFAULT_STATUS,
        "created_by": created_by or data.assignee,
    }
    db.table("versions").insert(ver_row).execute()

    return create_response(task, "Task created successfully")


# Update a task by UID
def update_task(uid: str, data: TaskUpdate) -> TaskOut:
    task = db_lookup("tasks", uid, name_column=None)
    updates = data.model_dump(exclude_none=True)

    if "project_uid" in updates:
        db_lookup("projects", updates["project_uid"])

    if not updates:
        return create_response(task, "Task updated successfully")

    result = db.table("tasks").update(updates).eq("uid", task["uid"]).execute()
    return create_response(result.data[0], "Task updated successfully")


# Delete a task by UID (soft delete)
def delete_task(uid: str) -> dict:
    db_lookup("tasks", uid, name_column=None)
    db.table("tasks").update({"deleted_at": "now()"}).eq("uid", uid).execute()
    return create_response(None, f"Task '{uid}' deleted successfully")


# Get a list of all tasks, with optional filtering (excluding soft-deleted)
def list_tasks(
        uid: str | None = None,
        project_uid: str | None = None,
        parent_type: str | None = None,
        parent_id: str | None = None,
        name: str | None = None,
        assignee: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    query = db.table("tasks").select("*", count="exact")

    if not include_deleted:
        query = query.is_("deleted_at", "null")
    if uid:
        query = query.eq("uid", uid)
    if project_uid:
        query = query.eq("project_uid", project_uid)
    if parent_type:
        query = query.eq("parent_type", parent_type)
    if parent_id:
        query = query.eq("parent_uid", parent_id)
    if name:
        query = query.ilike("name", f"%{name}%")
    if assignee:
        query = query.eq("assignee", assignee)
    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Tasks retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }


def list_task_versions(task_uid: str, limit: int = 50, offset: int = 0):
    db_lookup("tasks", task_uid, name_column=None)

    result = (
        db.table("versions")
        .select("*", count="exact")
        .eq("task_uid", task_uid)
        .order("vnum", desc=True)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    return {
        "status": "success",
        "message": "Task versions retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }
