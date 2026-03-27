from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from models import Base


class Shot(Base):
    __tablename__ = "shots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[str] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=False)
    seq: Mapped[str] = mapped_column(String, nullable=False)
    shot: Mapped[str] = mapped_column(String, nullable=False)
    frame_in: Mapped[int] = mapped_column(Integer, nullable=False)
    frame_out: Mapped[int] = mapped_column(Integer, nullable=False)
    fps: Mapped[Optional[float]] = mapped_column(nullable=True)
    colorspace: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    __table_args__ = (UniqueConstraint("project_uid", "seq", "shot", name="uq_shot_code"),)
