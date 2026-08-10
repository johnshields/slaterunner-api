from datetime import datetime

from pydantic import BaseModel, ConfigDict

from enums.pipeline.version_status import VersionStatus


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: str | None = None
    task_uid: str | None = None
    vnum: int
    status: VersionStatus
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime


class VersionCreate(BaseModel):
    uid: str | None = None
    project_uid: str
    task_uid: str
    vnum: int | None = None
    status: VersionStatus | None = VersionStatus.draft
    publish_type: str | None = None
    representation: str | None = None
    path: str | None = None
    meta: dict | None = {}


class VersionUpdate(BaseModel):
    uid: str | None = None
    project_uid: str | None = None
    task_uid: str | None = None
    status: VersionStatus | None = None
    created_by: str | None = None
