from fastapi import HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.pipeline.version import Version
from models.pipeline.task import Task
from models.pipeline.project import Project
from typing import Optional
from schemas.pipeline.task import TaskOut, TaskCreate, TaskUpdate
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid
from utils.datetime_helpers import now_utc

TASK_DEFAULT_STATUS = "WIP"
VERSION_DEFAULT_STATUS = "draft"


# Create a new task, generate a UID if not provided, and auto-create Version v1.
def create_task(db: Session, data: TaskCreate, *, created_by: str | None = None) -> TaskOut:
    # Validate project exists
    project = db_lookup(db, Project, data.project_uid)

    # Create and persist task
    uid = data.uid or generate_uid("TASK")
    new_task = Task(
        uid=uid,
        project_uid=project.uid,
        parent_type=data.parent_type,
        parent_uid=data.parent_uid,
        name=data.name,
        assignee=data.assignee,
        status=data.status or TASK_DEFAULT_STATUS,
    )

    try:
        # Validate task constraints
        db.add(new_task)
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Task violates a database constraint") from e

    try:
        # Auto-create initial version v1 with draft status
        create_task_version(
            db,
            task=new_task,
            status=VERSION_DEFAULT_STATUS,
            created_by=created_by or new_task.assignee,
            vnum=1,
        )
        # Validate version constraints
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create initial version") from e

    # Commit task and version atomically
    db.commit()
    db.refresh(new_task)
    return create_response(new_task, "Task created successfully")


# Create version for task with default status and version number
def create_task_version(
        db: Session,
        *,
        task: Task,
        status: str = VERSION_DEFAULT_STATUS,
        created_by: str | None = None,
        vnum: int = 1,
) -> Version:
    ver = Version(
        uid=generate_uid("VER"),
        project_uid=task.project_uid,
        task_uid=task.uid,
        vnum=vnum,
        status=status,
        created_by=created_by,
    )
    db.add(ver)
    return create_response(ver, "Task version created successfully")


# Update a task by UID
def update_task(db: Session, uid: str, data: TaskUpdate) -> TaskOut:
    # Locate task by UID
    task = db_lookup(db, Task, uid)

    # Update project association if provided
    if data.project_uid:
        project = db.scalar(select(Project).where(Project.uid == data.project_uid))
        if not project:
            raise HTTPException(status_code=404, detail="Target project not found")
        task.project_uid = project.uid

    # Update other fields if provided
    if data.parent_type is not None:
        task.parent_type = data.parent_type

    if data.parent_uid is not None:
        task.parent_uid = data.parent_uid

    if data.name is not None:
        task.name = data.name

    if data.assignee is not None:
        task.assignee = data.assignee

    if data.status is not None:
        task.status = data.status

    db.commit()
    db.refresh(task)
    return create_response(task, "Task updated successfully")


# Delete a task by UID (soft delete)
def delete_task(db: Session, uid: str) -> dict:
    task = db_lookup(db, Task, uid)
    
    # Soft delete: set deleted_at timestamp
    task.deleted_at = now_utc()
    
    db.commit()
    return create_response(None, f"Task '{uid}' deleted successfully")


# Get a list of all tasks, with optional filtering (excluding soft-deleted)
def list_tasks(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        parent_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        name: Optional[str] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    # Build base query with filters
    base_stmt = select(Task)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        base_stmt = base_stmt.where(Task.deleted_at.is_(None))

    if uid:
        base_stmt = base_stmt.where(Task.uid == uid)

    if project_uid:
        base_stmt = base_stmt.where(Task.project_uid == project_uid)

    if parent_type:
        base_stmt = base_stmt.where(Task.parent_type == parent_type)

    if parent_id:
        base_stmt = base_stmt.where(Task.parent_uid == parent_id)

    if name:
        base_stmt = base_stmt.where(Task.name.ilike(f"%{name}%"))

    if assignee:
        base_stmt = base_stmt.where(Task.assignee == assignee)

    if status:
        base_stmt = base_stmt.where(Task.status == status)

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Task.created_at.desc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Tasks retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }


def list_task_versions(
        db: Session,
        task_uid: str,
        limit: int = 50,
        offset: int = 0,
):
    db_lookup(db, Task, task_uid)

    base_stmt = select(Version).where(Version.task_uid == task_uid)

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Version.vnum.desc(), Version.created_at.desc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Task versions retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }
