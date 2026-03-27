from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from enums.pipeline.publish_type import PublishType
from enums.pipeline.representation import Representation


class PublishOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    version_uid: Optional[str] = None
    type: Optional[PublishType] = None
    representation: Optional[Representation] = None
    path: str
    meta: dict
    created_at: datetime
    updated_at: datetime


class PublishCreate(BaseModel):
    uid: Optional[str] = None
    project_uid: str
    version_uid: str
    type: PublishType
    representation: Optional[Representation] = None
    path: str
    meta: Optional[dict] = {}

    @field_validator("path")
    def validate_path(cls, v):
        if not v.strip():
            raise ValueError("Publish path cannot be empty")
        return v.strip()


class PublishUpdate(BaseModel):
    uid: Optional[str] = None
    type: Optional[PublishType] = None
    representation: Optional[Representation] = None
    path: Optional[str] = None
    meta: Optional[dict] = None
