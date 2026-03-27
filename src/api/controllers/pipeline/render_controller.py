from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.pipeline.render import RenderJob
from models.pipeline.project import Project
from schemas.pipeline.render import RenderJobOut, RenderJobCreate, RenderJobUpdate
from schemas.response import create_response
from typing import Optional
from utils.database import db_lookup
from utils.uid import generate_uid
from utils.datetime_helpers import now_utc


# Get a list of render jobs with optional filtering (excluding soft-deleted)
def list_render_jobs(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        adapter: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    # Build base query with filters
    base_stmt = select(RenderJob)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        base_stmt = base_stmt.where(RenderJob.deleted_at.is_(None))

    if uid:
        base_stmt = base_stmt.where(RenderJob.uid == uid)

    if project_uid:
        base_stmt = base_stmt.where(RenderJob.project_uid == project_uid)

    if adapter:
        base_stmt = base_stmt.where(RenderJob.adapter == adapter)

    if status:
        base_stmt = base_stmt.where(RenderJob.status == status)

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(RenderJob.submitted_at.desc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Render jobs retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }


# Create a new render job
def create_render_job(db: Session, data: RenderJobCreate) -> RenderJobOut:
    # Validate project exists
    project = db_lookup(db, Project, data.project_uid)
    
    # Generate UID if not provided
    uid = data.uid or generate_uid("RJ")
    
    # Create and persist render job
    new_render_job = RenderJob(
        uid=uid,
        project_uid=project.uid,
        context=data.context,
        adapter=data.adapter,
        status=data.status,
    )
    
    db.add(new_render_job)
    db.commit()
    db.refresh(new_render_job)
    
    return create_response(new_render_job, "Render job created successfully")


# Update a render job by UID
def update_render_job(db: Session, uid: str, data: RenderJobUpdate) -> RenderJobOut:
    # Locate render job by UID
    render_job = db_lookup(db, RenderJob, uid)
    
    # Update fields if provided
    if data.context is not None:
        render_job.context = data.context
    
    if data.adapter is not None:
        render_job.adapter = data.adapter
    
    if data.status is not None:
        render_job.status = data.status
    
    if data.logs is not None:
        render_job.logs = data.logs
    
    db.commit()
    db.refresh(render_job)
    return create_response(render_job, "Render job updated successfully")


# Delete a render job by UID (soft delete)
def delete_render_job(db: Session, uid: str) -> dict:
    render_job = db_lookup(db, RenderJob, uid)
    
    # Soft delete: set deleted_at timestamp
    render_job.deleted_at = now_utc()
    
    db.commit()
    return create_response(None, f"Render job '{uid}' deleted successfully")
