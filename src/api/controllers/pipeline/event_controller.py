from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.pipeline.event import Event
from models.pipeline.project import Project
from schemas.pipeline.event import EventOut, EventCreate, EventUpdate
from schemas.response import create_response
from typing import Optional
from utils.database import db_lookup
from utils.uid import generate_uid
from utils.datetime_helpers import now_utc


# Get a list of events with optional filtering (excluding soft-deleted)
def list_events(
        db: Session,
        uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        kind: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
) -> dict:
    # Build base query with filters
    base_stmt = select(Event)
    
    # Exclude soft-deleted records by default
    if not include_deleted:
        base_stmt = base_stmt.where(Event.deleted_at.is_(None))

    if uid:
        base_stmt = base_stmt.where(Event.uid == uid)

    if project_uid:
        base_stmt = base_stmt.where(Event.project_uid == project_uid)

    if kind:
        base_stmt = base_stmt.where(Event.kind == kind)

    # Get total count
    count = db.scalar(select(func.count()).select_from(base_stmt.subquery()))
    
    # Get paginated items
    stmt = base_stmt.order_by(Event.created_at.desc()).limit(limit).offset(offset)
    data = db.execute(stmt).scalars().all()
    
    return {
        "status": "success",
        "message": "Events retrieved successfully",
        "data": data,
        "count": count,
        "limit": limit,
        "offset": offset
    }


# Create a new event
def create_event(db: Session, data: EventCreate) -> EventOut:
    # Validate project exists
    project = db_lookup(db, Project, data.project_uid)
    
    # Generate UID if not provided
    uid = data.uid or generate_uid("EVENT")
    
    # Create and persist event
    new_event = Event(
        uid=uid,
        project_uid=project.uid,
        kind=data.kind,
        payload=data.payload,
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return create_response(new_event, "Event created successfully")


# Update an event by UID
def update_event(db: Session, uid: str, data: EventUpdate) -> EventOut:
    # Locate event by UID
    event = db_lookup(db, Event, uid)
    
    # Update fields if provided
    if data.kind is not None:
        event.kind = data.kind
    
    if data.payload is not None:
        event.payload = data.payload
    
    db.commit()
    db.refresh(event)
    return create_response(event, "Event updated successfully")


# Delete an event by UID (soft delete)
def delete_event(db: Session, uid: str) -> dict:
    event = db_lookup(db, Event, uid)
    
    # Soft delete: set deleted_at timestamp
    event.deleted_at = now_utc()
    
    db.commit()
    return create_response(None, f"Event '{uid}' deleted successfully")
