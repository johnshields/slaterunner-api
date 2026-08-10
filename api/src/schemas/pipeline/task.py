from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from enums.pipeline.parent_type import ParentType
from enums.pipeline.task_status import TaskStatus


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: str | None = None
    parent_type: ParentType
    parent_uid: str | None = None
    name: str
    assignee: str | None = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    uid: str | None = None
    project_uid: str
    parent_type: ParentType | None = None
    parent_uid: str | None = None
    name: str = Field(..., min_length=1, max_length=100)
    assignee: str | None = None
    status: TaskStatus | None = TaskStatus.WIP

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Task name cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    uid: str | None = None
    project_uid: str | None = None
    parent_type: ParentType | None = None
    parent_uid: str | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    assignee: str | None = None
    status: TaskStatus | None = None
