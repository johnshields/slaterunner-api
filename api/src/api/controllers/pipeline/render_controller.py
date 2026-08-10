
from clients.db import db
from schemas.pipeline.render import RenderJobCreate, RenderJobOut, RenderJobUpdate
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid


# Get a list of render jobs with optional filtering (excluding soft-deleted)
def list_render_jobs(
        uid: str | None = None,
        project_uid: str | None = None,
        adapter: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    query = db.table("render_jobs").select("*", count="exact")

    if not include_deleted:
        query = query.is_("deleted_at", "null")
    if uid:
        query = query.eq("uid", uid)
    if project_uid:
        query = query.eq("project_uid", project_uid)
    if adapter:
        query = query.eq("adapter", adapter)
    if status:
        query = query.eq("status", status)

    result = query.order("submitted_at", desc=True).range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Render jobs retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }


# Create a new render job
def create_render_job(data: RenderJobCreate) -> RenderJobOut:
    db_lookup("projects", data.project_uid)

    row = data.model_dump(exclude_none=True)
    row["uid"] = row.get("uid") or generate_uid("RJB")

    result = db.table("render_jobs").insert(row).execute()
    return create_response(result.data[0], "Render job created successfully")


# Update a render job by UID
def update_render_job(uid: str, data: RenderJobUpdate) -> RenderJobOut:
    render_job = db_lookup("render_jobs", uid, name_column=None)
    updates = data.model_dump(exclude_none=True)

    if not updates:
        return create_response(render_job, "Render job updated successfully")

    result = db.table("render_jobs").update(updates).eq("uid", render_job["uid"]).execute()
    return create_response(result.data[0], "Render job updated successfully")


# Delete a render job by UID (soft delete)
def delete_render_job(uid: str) -> dict:
    db_lookup("render_jobs", uid, name_column=None)
    db.table("render_jobs").update({"deleted_at": "now()"}).eq("uid", uid).execute()
    return create_response(None, f"Render job '{uid}' deleted successfully")
