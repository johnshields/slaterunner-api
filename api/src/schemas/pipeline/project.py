from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    name: str
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    uid: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()


class ProjectUpdate(BaseModel):
    uid: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class ProjectCounts(BaseModel):
    shots: int
    tasks: int


class ProjectOverviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    name: str
    counts: ProjectCounts
    created_at: datetime
