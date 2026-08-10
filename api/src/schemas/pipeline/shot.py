import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ShotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str
    project_uid: str | None = None
    seq: str
    shot: str
    frame_in: int
    frame_out: int
    fps: float | None = None
    colorspace: str | None = None
    created_at: datetime
    updated_at: datetime


class ShotCreate(BaseModel):
    uid: str | None = None
    project_uid: str
    seq: str = Field(..., min_length=1, max_length=20)
    shot: str = Field(..., min_length=1, max_length=20)
    frame_in: int = Field(..., ge=0)
    frame_out: int = Field(..., ge=0)
    fps: float | None = Field(None, ge=1.0, le=120.0)
    colorspace: str | None = None

    @field_validator("frame_out")
    def validate_frame_range(cls, v, values):
        if "frame_in" in values and v <= values["frame_in"]:
            raise ValueError("frame_out must be greater than frame_in")
        return v

    @field_validator("seq", "shot")
    def validate_identifiers(cls, v):
        if not re.match(r"^[A-Z0-9_]+$", v):
            raise ValueError("Must use uppercase letters, numbers, underscores")
        return v


class ShotUpdate(BaseModel):
    uid: str | None = None
    project_uid: str | None = None
    seq: str | None = None
    shot: str | None = None
    frame_in: int | None = None
    frame_out: int | None = None
    fps: float | None = None
    colorspace: str | None = None
