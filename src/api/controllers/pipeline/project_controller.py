from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.pipeline.publish import Publish
from models.pipeline.task import Task
from models.pipeline.shot import Shot
from models.pipeline.asset import Asset
from models.pipeline.project import Project
from typing import Optional
from schemas.pipeline.project import ProjectOut, ProjectCreate, ProjectUpdate, ProjectOverviewOut
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid
from utils.datetime_helpers import now_utc


# Create a new project, generate a UID if not provided
def create_project(db: Session, data: ProjectCreate) -> ProjectOut:
    # Validate project name is unique among non-deleted projects
    existing = db.scalar(
        select(Project).where(
            Project.name == data.name,
            Project.deleted_at.is_(None)
        )
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Project '{data.name}' already exists."
        )

    # Create and persist project
    uid = data.uid or generate_uid("PROJ")
    new_project = Project(uid=uid, name=data.name)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return create_response(new_project, "Project created successfully")


# Update a project by UID or name
def update_project(db: Session, identifier: str, data: ProjectUpdate) -> ProjectOut:
    project = db_lookup(db, Project, identifier)

    if data.name:
        project.name = data.name

    db.commit()
    db.refresh(project)
    return create_response(project, "Project updated successfully")


# Delete a project by UID or name (soft delete)
def delete_project(db: Session, identifier: str) -> dict:
    project = db_lookup(db, Project, identifier)
    
    # Soft delete: set deleted_at timestamp
    project.deleted_at = now_utc()
    
    db.commit()
    return create_response(None, f"Project '{identifier}' deleted successfully")


# Get a list of all projects, with optional filtering by UID or name (excluding soft-deleted)
def list_projects(
        db: Session,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    # Build base query with filters
    base_stmt = select(Project)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        base_stmt = base_stmt.where(Project.deleted_at.is_(None))

    if uid:
        base_stmt = base_stmt.where(Project.uid == uid)

    if name:
        base_stmt = base_stmt.where(Project.name.ilike(f"%{name}%"))

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Project.name.asc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Projects retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }


# Get basic counts and info for a single project
def list_project_overview(db: Session, project_uid: str) -> ProjectOverviewOut:
    project = db_lookup(db, Project, project_uid)

    # Count shots and tasks for the project
    shots_count = db.scalar(select(func.count()).select_from(Shot).where(Shot.project_uid == project_uid))
    tasks_count = db.scalar(
        select(func.count()).select_from(Task).where(
            Task.project_uid == project_uid,
            Task.parent_type == "shot"
        )
    )

    overview = ProjectOverviewOut(
        uid=project.uid,
        name=project.name,
        counts={"shots": shots_count, "tasks": tasks_count},
        created_at=project.created_at
    )
    return create_response(overview, "Project overview retrieved successfully")


# Get all assets belonging to a project
def list_project_assets(
        db: Session,
        project_uid: str,
        limit: int = 50,
        offset: int = 0,
):
    db_lookup(db, Project, project_uid)

    base_stmt = select(Asset).where(Asset.project_uid == project_uid)

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Asset.name.asc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Project assets retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }


# Get all shots in a project, with optional filtering by seq, shot, or frame range
def list_project_shots(
        db: Session,
        project_uid: str,
        seq: str = None,
        shot: str = None,
        range: str = None,
        limit: int = 50,
        offset: int = 0
):
    db_lookup(db, Project, project_uid)

    base_stmt = select(Shot).where(Shot.project_uid == project_uid)
    if seq:
        base_stmt = base_stmt.where(Shot.seq == seq)

    if shot:
        base_stmt = base_stmt.where(Shot.shot == shot)

    if range:
        try:
            start, end = map(int, range.split("-"))
            base_stmt = base_stmt.where(Shot.frame_in >= start, Shot.frame_out <= end)
        except ValueError:
            raise ValueError("Invalid range format. Use start-end (e.g. 100-200).")

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Shot.seq.asc(), Shot.shot.asc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Project shots retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }


# Get all tasks for a project, with optional filters for parent_type and status
def list_project_tasks(
        db: Session,
        project_uid: str,
        parent_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
):
    db_lookup(db, Project, project_uid)

    base_stmt = select(Task).where(Task.project_uid == project_uid)
    if parent_type:
        base_stmt = base_stmt.where(Task.parent_type == parent_type)

    if status:
        base_stmt = base_stmt.where(Task.status == status)

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Task.created_at.desc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Project tasks retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }


# Get all publishes for a project, optionally filtered by type and representation
def list_project_publishes(
        db: Session,
        project_uid: str,
        type: str = None,
        rep: str = None,
        limit: int = 50,
        offset: int = 0
):
    db_lookup(db, Project, project_uid)

    base_stmt = select(Publish).where(Publish.project_uid == project_uid)
    if type:
        base_stmt = base_stmt.where(Publish.type == type)

    if rep:
        base_stmt = base_stmt.where(Publish.representation == rep)

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Publish.created_at.desc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Project publishes retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }
