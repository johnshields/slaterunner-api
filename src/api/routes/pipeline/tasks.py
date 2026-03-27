from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from db.db import get_db
from schemas.pagination import PaginatedResponse
from schemas.response import ApiResponse
import api.controllers.pipeline.task_controller as controller
import schemas.pipeline.task as schemas_task
import schemas.pipeline.version as schemas_version

router = APIRouter()


@router.post("/tasks", response_model=ApiResponse[schemas_task.TaskOut], status_code=201)
def post_task(
        data: schemas_task.TaskCreate,
        db: Session = Depends(get_db),
):
    """Create a new Task with auto-generated initial Version."""
    return controller.create_task(db, data)


@router.patch("/tasks/{uid}", response_model=ApiResponse[schemas_task.TaskOut])
def patch_task(
        uid: str,
        data: schemas_task.TaskUpdate,
        db: Session = Depends(get_db),
):
    """Update a Task by UID."""
    return controller.update_task(db, uid, data)


@router.delete("/tasks/{uid}")
def delete_task(
        uid: str,
        db: Session = Depends(get_db),
):
    """Delete a Task by UID."""
    return controller.delete_task(db, uid)


@router.get("/tasks", response_model=PaginatedResponse[schemas_task.TaskOut])
def get_tasks(
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        parent_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        name: Optional[str] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
        db: Session = Depends(get_db),
):
    """List or search Tasks with optional filters (excludes soft-deleted by default)."""
    return controller.list_tasks(db, uid, project_uid, parent_type, parent_id, name, assignee, status, limit, offset, include_deleted)


@router.get("/tasks/{task_uid}/versions", response_model=PaginatedResponse[schemas_version.VersionOut])
def get_task_versions(
        task_uid: str,
        db: Session = Depends(get_db),
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0)
):
    """List all Versions for a Task. Returns paginated results with metadata."""
    return controller.list_task_versions(db, task_uid, limit, offset)
