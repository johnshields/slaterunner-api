from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, func, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column
from models import Base
from enums.pipeline.asset_type import AssetType


class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    project_uid: Mapped[str] = mapped_column(ForeignKey("projects.uid", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[Optional[AssetType]] = mapped_column(Enum(AssetType), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    __table_args__ = (UniqueConstraint("project_uid", "name", name="uq_asset_project_name"),)
