from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, ForeignKey, Text, TIMESTAMP, func, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from models import Base
from enums.pipeline.publish_type import PublishType
from enums.pipeline.representation import Representation


class Publish(Base):
    __tablename__ = "publishes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    version_uid: Mapped[str] = mapped_column(ForeignKey("versions.uid", ondelete="CASCADE"), nullable=False)
    project_uid: Mapped[Optional[str]] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=False)
    type: Mapped[PublishType] = mapped_column(Enum(PublishType), nullable=False)
    representation: Mapped[Optional[Representation]] = mapped_column(Enum(Representation), nullable=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
