"""Schemas for Smart Notulen."""
import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class NotulenCreate(BaseModel):
    """
    Input dari Flutter: transcript sudah diproses oleh Speech-to-Text di sisi klien.
    Backend hanya menerima teks mentah hasil transkripsi.
    """
    transcript: str = Field(..., min_length=1, description="Teks hasil Speech-to-Text dari Flutter")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Durasi rekaman dalam detik")


class NotulenSave(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    meeting_date: Optional[datetime] = None


class NotulenResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    transcript: Optional[str]
    summary: Optional[str]
    action_items: Optional[Any]
    duration_seconds: Optional[int]
    audio_url: Optional[str]
    meeting_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotulenListItem(BaseModel):
    id: uuid.UUID
    title: str
    meeting_date: Optional[datetime]
    duration_seconds: Optional[int]
    has_summary: bool
    created_at: datetime

    model_config = {"from_attributes": True}
