from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
from schemas.pagination import PaginatedResponse
from schemas.response import ApiResponse
import api.controllers.pipeline.render_controller as controller
import schemas.pipeline.render as schemas_render

router = APIRouter()


@router.get("/renders", response_model=PaginatedResponse[schemas_render.RenderJobOut])
def get_render_jobs(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        adapter: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
        db: Session = Depends(get_db),
):
    """List or search Render Jobs with optional filters (excludes soft-deleted by default)."""
    return controller.list_render_jobs(db, uid, project_uid, adapter, status, limit, offset, include_deleted)


@router.post("/renders", response_model=ApiResponse[schemas_render.RenderJobOut], status_code=201)
def post_render_job(
        data: schemas_render.RenderJobCreate,
        db: Session = Depends(get_db)
):
    """Create a new Render Job."""
    return controller.create_render_job(db, data)


@router.patch("/renders/{uid}", response_model=ApiResponse[schemas_render.RenderJobOut])
def patch_render_job(
        uid: str,
        data: schemas_render.RenderJobUpdate,
        db: Session = Depends(get_db),
):
    """Update a Render Job by UID."""
    return controller.update_render_job(db, uid, data)


@router.delete("/renders/{uid}")
def delete_render_job(
        uid: str,
        db: Session = Depends(get_db),
):
    """Delete a Render Job by UID."""
    return controller.delete_render_job(db, uid)
