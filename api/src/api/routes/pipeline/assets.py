
from fastapi import APIRouter, Query

import api.controllers.pipeline.asset_controller as controller
import schemas.pipeline.asset as schemas_asset
import schemas.pipeline.task as schemas_task
from schemas.pagination import PaginatedResponse
from schemas.response import ApiResponse

router = APIRouter()


@router.post("/assets", response_model=ApiResponse[schemas_asset.AssetOut], status_code=201)
def post_asset(data: schemas_asset.AssetCreate):
    """Create a new Asset."""
    return controller.create_asset(data)


@router.patch("/assets/{identifier}", response_model=ApiResponse[schemas_asset.AssetOut])
def patch_asset(identifier: str, data: schemas_asset.AssetUpdate):
    """Update an Asset by UID or name."""
    return controller.update_asset(identifier, data)


@router.delete("/assets/{identifier}")
def delete_asset(identifier: str):
    """Delete an Asset by UID or name."""
    return controller.delete_asset(identifier)


@router.get("/assets", response_model=PaginatedResponse[schemas_asset.AssetOut])
def get_assets(
        uid: str | None = None,
        project_uid: str | None = None,
        name: str | None = None,
        type: str | None = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
):
    """List or search Assets with optional filters (excludes soft-deleted by default)."""
    return controller.list_assets(uid, project_uid, name, type, limit, offset, include_deleted)


@router.get("/assets/{asset_uid}/tasks", response_model=PaginatedResponse[schemas_task.TaskOut])
def get_asset_tasks(
        asset_uid: str,
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
):
    """List all Tasks for an Asset. Returns paginated results with metadata."""
    return controller.list_asset_tasks(asset_uid, limit, offset)
