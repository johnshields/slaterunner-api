from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: str | None = None
    kind: str
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class EventCreate(BaseModel):
    uid: str | None = None
    project_uid: str
    kind: str
    payload: dict[str, Any]

    @field_validator("kind")
    def validate_kind(cls, v):
        if not v.strip():
            raise ValueError("Event kind cannot be empty")
        return v.strip()


class EventUpdate(BaseModel):
    uid: str | None = None
    kind: str | None = None
    payload: dict[str, Any] | None = None
