from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from enums.pipeline.publish_type import PublishType
from enums.pipeline.representation import Representation


class PublishOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    uid: str
    project_uid: str | None = None
    version_uid: str | None = None
    type: PublishType | None = None
    representation: Representation | None = None
    path: str
    # DB column is "metadata"; exposed as "meta" in the API contract
    meta: dict = Field(validation_alias="metadata")
    created_at: datetime
    updated_at: datetime


class PublishCreate(BaseModel):
    uid: str | None = None
    project_uid: str
    version_uid: str
    type: PublishType
    representation: Representation | None = None
    path: str
    meta: dict | None = {}

    @field_validator("path")
    def validate_path(cls, v):
        if not v.strip():
            raise ValueError("Publish path cannot be empty")
        return v.strip()


class PublishUpdate(BaseModel):
    uid: str | None = None
    type: PublishType | None = None
    representation: Representation | None = None
    path: str | None = None
    meta: dict | None = None
