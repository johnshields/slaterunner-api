from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.db import get_db
from schemas.pagination import PaginatedResponse
from schemas.response import ApiResponse
import api.controllers.pipeline.event_controller as controller
import schemas.pipeline.event as schemas_event

router = APIRouter()


@router.get("/events", response_model=PaginatedResponse[schemas_event.EventOut])
def get_events(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        kind: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
        db: Session = Depends(get_db),
):
    """List or search Events with optional filters (excludes soft-deleted by default)."""
    return controller.list_events(db, uid, project_uid, kind, limit, offset, include_deleted)


@router.post("/events", response_model=ApiResponse[schemas_event.EventOut], status_code=201)
def post_event(
        data: schemas_event.EventCreate,
        db: Session = Depends(get_db)
):
    """Create a new Event."""
    return controller.create_event(db, data)


@router.patch("/events/{uid}", response_model=ApiResponse[schemas_event.EventOut])
def patch_event(
        uid: str,
        data: schemas_event.EventUpdate,
        db: Session = Depends(get_db),
):
    """Update an Event by UID."""
    return controller.update_event(db, uid, data)


@router.delete("/events/{uid}")
def delete_event(
        uid: str,
        db: Session = Depends(get_db),
):
    """Delete an Event by UID."""
    return controller.delete_event(db, uid)
