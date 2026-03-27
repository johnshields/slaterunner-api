from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, func, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column
from models import Base
from enums.pipeline.version_status import VersionStatus


class Version(Base):
    __tablename__ = "versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    project_uid: Mapped[str] = mapped_column(
        ForeignKey("projects.uid", ondelete="CASCADE"), nullable=False
    )
    task_uid: Mapped[str] = mapped_column(
        ForeignKey("tasks.uid", ondelete="CASCADE"), nullable=False
    )

    vnum: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[VersionStatus] = mapped_column(Enum(VersionStatus), nullable=False, default=VersionStatus.draft)
    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("task_uid", "vnum", name="uq_version_per_task"),)
