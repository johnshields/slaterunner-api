from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enums.pipeline.version_status import VersionStatus


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    task_uid: Optional[str] = None
    vnum: int
    status: VersionStatus
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class VersionCreate(BaseModel):
    uid: Optional[str] = None
    project_uid: str
    task_uid: str
    vnum: Optional[int] = None
    status: Optional[VersionStatus] = VersionStatus.draft
    publish_type: Optional[str] = None
    representation: Optional[str] = None
    path: Optional[str] = None
    meta: Optional[dict] = {}


class VersionUpdate(BaseModel):
    uid: Optional[str] = None
    project_uid: Optional[str] = None
    task_uid: Optional[str] = None
    status: Optional[VersionStatus] = None
    created_by: Optional[str] = None
