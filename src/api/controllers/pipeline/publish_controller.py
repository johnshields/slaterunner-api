from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.pipeline.publish import Publish
from models.pipeline.project import Project
from models.pipeline.version import Version
from schemas.pipeline.publish import PublishOut, PublishCreate, PublishUpdate
from schemas.response import create_response
from typing import Optional
from utils.database import db_lookup
from utils.uid import generate_uid
from utils.datetime_helpers import now_utc


# Create a new publish
def create_publish(db: Session, data: PublishCreate) -> PublishOut:
    # Validate project and version exist
    project = db_lookup(db, Project, data.project_uid)
    version = db_lookup(db, Version, data.version_uid)

    # Generate UID if not provided
    uid = data.uid or generate_uid("PUB")
    
    # Create and persist publish
    new_publish = Publish(
        uid=uid,
        project_uid=project.uid,
        version_uid=version.uid,
        type=data.type,
        representation=data.representation,
        path=data.path,
        meta=data.meta or {},
    )
    
    db.add(new_publish)
    db.commit()
    db.refresh(new_publish)
    
    return create_response(new_publish, "Publish created successfully")


# Update a publish by UID
def update_publish(db: Session, uid: str, data: PublishUpdate) -> PublishOut:
    # Locate publish by UID
    publish = db_lookup(db, Publish, uid)
    
    # Update fields if provided
    if data.type is not None:
        publish.type = data.type
    
    if data.representation is not None:
        publish.representation = data.representation
    
    if data.path is not None:
        publish.path = data.path
    
    if data.meta is not None:
        publish.meta = data.meta
    
    db.commit()
    db.refresh(publish)
    return create_response(publish, "Publish updated successfully")


# Delete a publish by UID (soft delete)
def delete_publish(db: Session, uid: str) -> dict:
    publish = db_lookup(db, Publish, uid)
    
    # Soft delete: set deleted_at timestamp
    publish.deleted_at = now_utc()
    
    db.commit()
    return create_response(None, f"Publish '{uid}' deleted successfully")


# Get a list of all publishes, with optional filtering (excluding soft-deleted)
def list_publishes(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        version_uid: Optional[str] = None,
        type: Optional[str] = None,
        representation: Optional[str] = None,
        path: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    # Build base query with filters
    base_stmt = select(Publish)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        base_stmt = base_stmt.where(Publish.deleted_at.is_(None))

    if uid:
        base_stmt = base_stmt.where(Publish.uid == uid)

    if project_uid:
        base_stmt = base_stmt.where(Publish.project_uid == project_uid)

    if version_uid:
        base_stmt = base_stmt.where(Publish.version_uid == version_uid)

    if type:
        base_stmt = base_stmt.where(Publish.type == type)

    if representation:
        base_stmt = base_stmt.where(Publish.representation == representation)

    if path:
        base_stmt = base_stmt.where(Publish.path.ilike(f"%{path}%"))

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Publish.created_at.desc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Publishes retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }
