from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.pipeline.task import Task
from models.pipeline.asset import Asset
from models.pipeline.project import Project
from schemas.pipeline.task import TaskOut
from schemas.pipeline.asset import AssetOut, AssetCreate, AssetUpdate
from schemas.response import create_response
from utils.database import db_lookup
from utils.uid import generate_uid
from utils.datetime_helpers import now_utc


# Create a new asset, generate a UID if not provided.
def create_asset(db: Session, data: AssetCreate) -> AssetOut:
    # Validate project exists
    project = db_lookup(db, Project, data.project_uid)

    # Validate asset name is unique within project among non-deleted assets
    existing = db.scalar(
        select(Asset).where(
            Asset.project_uid == data.project_uid,
            Asset.name == data.name,
            Asset.deleted_at.is_(None)
        )
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Asset '{data.name}' already exists in project '{data.project_uid}'."
        )

    # Create and persist asset
    uid = data.uid or generate_uid("ASSET")
    new_asset = Asset(uid=uid, project_uid=project.uid, name=data.name, type=data.type)
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return create_response(new_asset, "Asset created successfully")


# Update an asset by UID or name
def update_asset(db: Session, identifier: str, data: AssetUpdate) -> AssetOut:
    # Locate asset by UID or name
    asset = db_lookup(db, Asset, identifier)

    # Update project association if provided
    if data.project_uid:
        project = db.scalar(select(Project).where(Project.uid == data.project_uid))
        if not project:
            raise HTTPException(status_code=404, detail="Target project not found")
        asset.project_uid = project.uid

    # Update other fields if provided
    if data.name:
        asset.name = data.name

    if data.type:
        asset.type = data.type

    db.commit()
    db.refresh(asset)
    return create_response(asset, "Asset updated successfully")


# Delete an asset by UID or name (soft delete)
def delete_asset(db: Session, identifier: str) -> dict:
    asset = db_lookup(db, Asset, identifier)
    
    # Soft delete: set deleted_at timestamp
    asset.deleted_at = now_utc()
    
    db.commit()
    return create_response(None, f"Asset '{identifier}' deleted successfully")


# Get a list of all assets, with optional filtering (excluding soft-deleted)
def list_assets(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    # Build base query with filters
    base_stmt = select(Asset)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        base_stmt = base_stmt.where(Asset.deleted_at.is_(None))

    if uid:
        base_stmt = base_stmt.where(Asset.uid == uid)

    if project_uid:
        base_stmt = base_stmt.where(Asset.project_uid == project_uid)

    if name:
        base_stmt = base_stmt.where(Asset.name.ilike(f"%{name}%"))

    if type:
        base_stmt = base_stmt.where(Asset.type == type)

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Asset.name.asc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Assets retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }


# Get all tasks belonging to an asset
def list_asset_tasks(db: Session, asset_uid: str, limit: int = 50, offset: int = 0):
    db_lookup(db, Asset, asset_uid)

    base_stmt = select(Task).where(
        Task.parent_type == "asset", Task.parent_uid == asset_uid
    )

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Task.name.asc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Asset tasks retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }
