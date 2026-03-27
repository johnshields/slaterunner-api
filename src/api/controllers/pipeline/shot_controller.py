from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.pipeline.shot import Shot
from models.pipeline.project import Project
from typing import Optional
from schemas.pipeline.shot import ShotCreate, ShotUpdate, ShotOut
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid
from utils.datetime_helpers import now_utc


# Create a new shot, generate a UID if not provided.
def create_shot(db: Session, data: ShotCreate) -> ShotOut:
    # Validate project exists
    project = db_lookup(db, Project, data.project_uid)

    # Validate shot is unique within project among non-deleted shots
    existing = db.scalar(
        select(Shot).where(
            Shot.project_uid == data.project_uid,
            Shot.seq == data.seq,
            Shot.shot == data.shot,
            Shot.deleted_at.is_(None)
        )
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Shot '{data.seq}/{data.shot}' already exists in project '{data.project_uid}'."
        )

    # Create and persist shot
    uid = data.uid or generate_uid("SHOT")
    new_shot = Shot(
        uid=uid,
        project_uid=project.uid,
        shot=data.shot,
        seq=data.seq,
        frame_in=data.frame_in,
        frame_out=data.frame_out,
        fps=data.fps,
        colorspace=data.colorspace,
    )
    db.add(new_shot)
    db.commit()
    db.refresh(new_shot)

    return create_response(new_shot, "Shot created successfully")


# Update a shot by UID
def update_shot(db: Session, uid: str, data: ShotUpdate) -> ShotOut:
    # Locate shot by UID
    shot = db_lookup(db, Shot, uid)

    # Update project association if provided
    if data.project_uid:
        project = db.scalar(select(Project).where(Project.uid == data.project_uid))
        if not project:
            raise HTTPException(status_code=404, detail="Target project not found")
        shot.project_uid = project.uid

    # Update other fields if provided
    if data.shot:
        shot.shot = data.shot

    if data.seq:
        shot.seq = data.seq

    if data.frame_in:
        shot.frame_in = data.frame_in

    if data.frame_out:
        shot.frame_out = data.frame_out

    if data.fps:
        shot.fps = data.fps

    if data.colorspace:
        shot.colorspace = data.colorspace

    db.commit()
    db.refresh(shot)
    return create_response(shot, "Shot updated successfully")


# Delete a shot by UID (soft delete)
def delete_shot(db: Session, uid: str) -> dict:
    shot = db_lookup(db, Shot, uid)
    
    # Soft delete: set deleted_at timestamp
    shot.deleted_at = now_utc()
    
    db.commit()
    return create_response(None, f"Shot '{uid}' deleted successfully")


# Get a list of shots, with optional filtering (excluding soft-deleted)
def list_shots(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        shot: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    # Build base query with filters
    base_stmt = select(Shot)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        base_stmt = base_stmt.where(Shot.deleted_at.is_(None))

    if uid:
        base_stmt = base_stmt.where(Shot.uid == uid)

    if project_uid:
        base_stmt = base_stmt.where(Shot.project_uid == project_uid)

    if shot:
        base_stmt = base_stmt.where(Shot.shot.ilike(f"%{shot}%"))

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Shot.shot.asc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Shots retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }
