from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional
from api.controllers.pipeline.task_controller import VERSION_DEFAULT_STATUS
from models.pipeline.publish import Publish
from models.pipeline.version import Version
from models.pipeline.task import Task
from models.pipeline.project import Project
from schemas.pipeline.version import VersionOut, VersionCreate, VersionUpdate
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid
from utils.datetime_helpers import now_utc


def create_version(
        db: Session,
        data: VersionCreate,
        *,
        publish: bool = False,
        created_by: str | None = None,
) -> VersionOut:
    # Validate project and task exist
    project = db_lookup(db, Project, data.project_uid)
    task = db_lookup(db, Task, data.task_uid)

    # Calculate next version number if not provided
    if data.vnum is None:
        max_vnum = db.scalar(
            select(func.max(Version.vnum)).where(Version.task_uid == task.uid)
        )
        vnum = (max_vnum or 0) + 1
    else:
        vnum = data.vnum

    version = Version(
        uid=generate_uid("VER"),
        project_uid=project.uid,
        task_uid=task.uid,
        vnum=vnum,
        status=data.status or VERSION_DEFAULT_STATUS,
        created_by=created_by,
    )

    db.add(version)
    db.flush()

    if publish:
        publish = Publish(
            uid=generate_uid("PUB"),
            project_uid=project.uid,
            version_uid=version.uid,
            type=data.publish_type,
            representation=data.representation,
            path=data.path or "",
            meta=data.meta or {},
        )
        db.add(publish)
        db.flush()

    db.commit()
    db.refresh(version)
    return create_response(version, "Version created successfully")


# Update a version by UID
def update_version(db: Session, uid: str, data: VersionUpdate) -> VersionOut:
    # Locate version by UID
    version = db_lookup(db, Version, uid)

    # Update project association if provided
    if data.project_uid:
        project = db.scalar(select(Project).where(Project.uid == data.project_uid))
        if not project:
            raise HTTPException(status_code=404, detail="Target project not found")
        version.project_uid = project.uid

    # Update task association if provided
    if data.task_uid:
        task = db.scalar(select(Task).where(Task.uid == data.task_uid))
        if not task:
            raise HTTPException(status_code=404, detail="Target task not found")
        version.task_uid = task.uid

    # Update other fields if provided
    if data.status is not None:
        version.status = data.status

    if data.created_by is not None:
        version.created_by = data.created_by

    db.commit()
    db.refresh(version)
    return create_response(version, "Version updated successfully")


def delete_version(db: Session, uid: str) -> dict:
    version = db_lookup(db, Version, uid)
    
    # Soft delete: set deleted_at timestamp
    version.deleted_at = now_utc()
    
    db.commit()
    return create_response(None, f"Version '{uid}' deleted successfully")


# Get a list of all versions, with optional filtering (excluding soft-deleted)
def list_versions(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        task_uid: Optional[str] = None,
        vnum: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    # Build base query with filters
    base_stmt = select(Version)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        base_stmt = base_stmt.where(Version.deleted_at.is_(None))

    if uid:
        base_stmt = base_stmt.where(Version.uid == uid)
    if project_uid:
        base_stmt = base_stmt.where(Version.project_uid == project_uid)
    if task_uid:
        base_stmt = base_stmt.where(Version.task_uid == task_uid)
    if vnum is not None:
        base_stmt = base_stmt.where(Version.vnum == vnum)
    if status:
        base_stmt = base_stmt.where(Version.status == status)
    if created_by:
        base_stmt = base_stmt.where(Version.created_by == created_by)

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Version.created_at.desc()).limit(limit).offset(offset)
    data = db.scalars(stmt).all()
    
    return {
        "status": "success",
        "message": "Versions retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }
