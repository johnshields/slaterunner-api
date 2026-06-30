from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from enums.pipeline.render_job_status import RenderJobStatus


class RenderJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: Optional[str] = None
    context: Dict[str, Any]
    adapter: str
    status: RenderJobStatus
    logs: Optional[str] = None
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime


class RenderJobCreate(BaseModel):
    uid: Optional[str] = None
    project_uid: str
    context: Dict[str, Any]
    adapter: str
    status: RenderJobStatus = RenderJobStatus.queued


class RenderJobUpdate(BaseModel):
    uid: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    adapter: Optional[str] = None
    status: Optional[RenderJobStatus] = None
    logs: Optional[str] = None
