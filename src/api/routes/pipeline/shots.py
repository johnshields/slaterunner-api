from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
from schemas.pagination import PaginatedResponse
from schemas.response import ApiResponse
import api.controllers.pipeline.shot_controller as controller
import schemas.pipeline.shot as schemas_shot

router = APIRouter()


@router.post("/shots", response_model=ApiResponse[schemas_shot.ShotOut], status_code=201)
def post_shot(
        data: schemas_shot.ShotCreate,
        db: Session = Depends(get_db)
):
    """Create a new Shot."""
    return controller.create_shot(db, data)


@router.patch("/shots/{shot_uid}", response_model=ApiResponse[schemas_shot.ShotOut])
def patch_shot(
        shot_uid: str,
        data: schemas_shot.ShotUpdate,
        db: Session = Depends(get_db),
):
    """Update a Shot by UID."""
    return controller.update_shot(db, shot_uid, data)


@router.delete("/shots/{shot_uid}")
def delete_shot(
        shot_uid: str,
        db: Session = Depends(get_db),
):
    """Delete a Shot by UID."""
    return controller.delete_shot(db, shot_uid)


@router.get("/shots", response_model=PaginatedResponse[schemas_shot.ShotOut])
def get_shots(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        shot: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
        db: Session = Depends(get_db),
):
    """List or search Shots with optional filters (excludes soft-deleted by default)."""
    return controller.list_shots(db, uid, project_uid, shot, limit, offset, include_deleted)
