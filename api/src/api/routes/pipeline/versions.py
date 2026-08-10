
from fastapi import APIRouter, Query

import api.controllers.pipeline.version_controller as controller
import schemas.pipeline.version as schemas_version
from schemas.pagination import PaginatedResponse
from schemas.response import ApiResponse

router = APIRouter()


@router.post("/versions", response_model=ApiResponse[schemas_version.VersionOut], status_code=201)
def post_version(
        data: schemas_version.VersionCreate,
        publish: bool = Query(default=False, description="Also create an initial publish"),
):
    """Create a new Version with optional auto-generated Publish."""
    return controller.create_version(data, publish=publish)


@router.patch("/versions/{uid}", response_model=ApiResponse[schemas_version.VersionOut])
def patch_version(uid: str, data: schemas_version.VersionUpdate):
    """Update a Version by UID."""
    return controller.update_version(uid, data)


@router.delete("/versions/{uid}")
def delete_version(uid: str):
    """Delete a Version by UID."""
    return controller.delete_version(uid)


@router.get("/versions", response_model=PaginatedResponse[schemas_version.VersionOut])
def get_versions(
        uid: str | None = None,
        project_uid: str | None = None,
        task_uid: str | None = None,
        vnum: int | None = None,
        status: str | None = None,
        created_by: str | None = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
):
    """List or search Versions with optional filters (excludes soft-deleted by default)."""
    return controller.list_versions(uid, project_uid, task_uid, vnum, status, created_by, limit, offset, include_deleted)
