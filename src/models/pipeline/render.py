from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Integer, String, ForeignKey, Text, TIMESTAMP, func, CheckConstraint, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from models import Base
from enums.pipeline.render_job_status import RenderJobStatus


class RenderJob(Base):
    __tablename__ = "render_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[Optional[str]] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=False)
    context: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    adapter: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[RenderJobStatus] = mapped_column(Enum(RenderJobStatus), nullable=False, default=RenderJobStatus.queued)
    logs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
