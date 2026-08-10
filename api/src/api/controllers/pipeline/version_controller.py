
from api.controllers.pipeline.task_controller import VERSION_DEFAULT_STATUS
from clients.db import db
from schemas.pipeline.version import VersionCreate, VersionOut, VersionUpdate
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid


def create_version(data: VersionCreate, *, publish: bool = False, created_by: str | None = None) -> VersionOut:
    project = db_lookup("projects", data.project_uid)
    task = db_lookup("tasks", data.task_uid, name_column=None)

    # Calculate next version number if not provided
    if data.vnum is None:
        max_result = (
            db.table("versions")
            .select("vnum")
            .eq("task_uid", task["uid"])
            .order("vnum", desc=True)
            .limit(1)
            .execute()
        )
        vnum = (max_result.data[0]["vnum"] if max_result.data else 0) + 1
    else:
        vnum = data.vnum

    ver_row = data.model_dump(include={"status"}, exclude_none=True)
    ver_row.update({
        "uid": generate_uid("VER"),
        "project_uid": project["uid"],
        "task_uid": task["uid"],
        "vnum": vnum,
        "created_by": created_by,
    })
    ver_row.setdefault("status", VERSION_DEFAULT_STATUS)

    result = db.table("versions").insert(ver_row).execute()
    version = result.data[0]

    if publish:
        pub_row = {
            "uid": generate_uid("PUB"),
            "project_uid": project["uid"],
            "version_uid": version["uid"],
            "type": data.publish_type,
            "representation": data.representation,
            "path": data.path or "",
            "metadata": data.meta or {},
        }
        db.table("publishes").insert(pub_row).execute()

    return create_response(version, "Version created successfully")


# Update a version by UID
def update_version(uid: str, data: VersionUpdate) -> VersionOut:
    version = db_lookup("versions", uid, name_column=None)
    updates = data.model_dump(exclude_none=True)

    if "project_uid" in updates:
        db_lookup("projects", updates["project_uid"])
    if "task_uid" in updates:
        db_lookup("tasks", updates["task_uid"], name_column=None)

    if not updates:
        return create_response(version, "Version updated successfully")

    result = db.table("versions").update(updates).eq("uid", version["uid"]).execute()
    return create_response(result.data[0], "Version updated successfully")


def delete_version(uid: str) -> dict:
    db_lookup("versions", uid, name_column=None)
    db.table("versions").update({"deleted_at": "now()"}).eq("uid", uid).execute()
    return create_response(None, f"Version '{uid}' deleted successfully")


# Get a list of all versions, with optional filtering (excluding soft-deleted)
def list_versions(
        uid: str | None = None,
        project_uid: str | None = None,
        task_uid: str | None = None,
        vnum: int | None = None,
        status: str | None = None,
        created_by: str | None = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    query = db.table("versions").select("*", count="exact")

    if not include_deleted:
        query = query.is_("deleted_at", "null")
    if uid:
        query = query.eq("uid", uid)
    if project_uid:
        query = query.eq("project_uid", project_uid)
    if task_uid:
        query = query.eq("task_uid", task_uid)
    if vnum is not None:
        query = query.eq("vnum", vnum)
    if status:
        query = query.eq("status", status)
    if created_by:
        query = query.eq("created_by", created_by)

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

    return {
        "status": "success",
        "message": "Versions retrieved successfully",
        "data": result.data,
        "count": result.count or 0,
        "limit": limit,
        "offset": offset,
    }
