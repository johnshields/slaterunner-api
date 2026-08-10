from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from enums.pipeline.asset_type import AssetType
from utils.validation import normalize_input


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: str | None = None
    name: str
    type: AssetType | None
    created_at: datetime
    updated_at: datetime


class AssetCreate(BaseModel):
    uid: str | None = None
    project_uid: str
    name: str = Field(..., min_length=1, max_length=100)
    type: AssetType | None = None

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Asset name cannot be empty")
        return v.strip()

    @field_validator("type", mode="before")
    def normalize_type(cls, v):
        return normalize_input(v, AssetType)


class AssetUpdate(BaseModel):
    uid: str | None = None
    project_uid: str | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    type: AssetType | None = None

    @field_validator("type", mode="before")
    def normalize_type(cls, v):
        return normalize_input(v, AssetType)
