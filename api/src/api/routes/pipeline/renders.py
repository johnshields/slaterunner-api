
from fastapi import APIRouter, Query

import api.controllers.pipeline.render_controller as controller
import schemas.pipeline.render as schemas_render
from schemas.pagination import PaginatedResponse
from schemas.response import ApiResponse

router = APIRouter()


@router.get("/renders", response_model=PaginatedResponse[schemas_render.RenderJobOut])
def get_render_jobs(
        uid: str | None = None,
        project_uid: str | None = None,
        adapter: str | None = None,
        status: str | None = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
):
    """List or search Render Jobs with optional filters (excludes soft-deleted by default)."""
    return controller.list_render_jobs(uid, project_uid, adapter, status, limit, offset, include_deleted)


@router.post("/renders", response_model=ApiResponse[schemas_render.RenderJobOut], status_code=201)
def post_render_job(data: schemas_render.RenderJobCreate):
    """Create a new Render Job."""
    return controller.create_render_job(data)


@router.patch("/renders/{uid}", response_model=ApiResponse[schemas_render.RenderJobOut])
def patch_render_job(uid: str, data: schemas_render.RenderJobUpdate):
    """Update a Render Job by UID."""
    return controller.update_render_job(uid, data)


@router.delete("/renders/{uid}")
def delete_render_job(uid: str):
    """Delete a Render Job by UID."""
    return controller.delete_render_job(uid)
