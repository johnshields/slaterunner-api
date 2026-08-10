from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from enums.pipeline.render_job_status import RenderJobStatus


class RenderJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: str | None = None
    context: dict[str, Any]
    adapter: str
    status: RenderJobStatus
    logs: str | None = None
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime


class RenderJobCreate(BaseModel):
    uid: str | None = None
    project_uid: str
    context: dict[str, Any]
    adapter: str
    status: RenderJobStatus = RenderJobStatus.queued


class RenderJobUpdate(BaseModel):
    uid: str | None = None
    context: dict[str, Any] | None = None
    adapter: str | None = None
    status: RenderJobStatus | None = None
    logs: str | None = None
