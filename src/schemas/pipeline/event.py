from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, field_validator


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    kind: str
    payload: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class EventCreate(BaseModel):
    uid: Optional[str] = None
    project_uid: str
    kind: str
    payload: Dict[str, Any]

    @field_validator("kind")
    def validate_kind(cls, v):
        if not v.strip():
            raise ValueError("Event kind cannot be empty")
        return v.strip()


class EventUpdate(BaseModel):
    uid: Optional[str] = None
    kind: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
