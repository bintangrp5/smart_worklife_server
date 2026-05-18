"""Schemas for Smart Pomodoro."""
import uuid
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class PomodoroSettingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    mode: str
    focus_duration_minutes: int
    break_duration_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PomodoroSettingUpdate(BaseModel):
    focus_duration_minutes: int = Field(..., ge=1, le=300)
    break_duration_minutes: int = Field(..., ge=1, le=120)


class PomodoroSessionStart(BaseModel):
    mode: str = Field(..., pattern="^(classic|deep_work|extend)$")
    session_type: str = Field(..., pattern="^(focus|break)$")
    duration_seconds: int = Field(..., ge=60)
    setting_id: Optional[uuid.UUID] = None


class PomodoroSessionEnd(BaseModel):
    actual_duration_seconds: int = Field(..., ge=0)
    status: str = Field(..., pattern="^(completed|cancelled)$")


class PomodoroSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    setting_id: Optional[uuid.UUID]
    mode: str
    session_type: str
    duration_seconds: int
    actual_duration_seconds: Optional[int]
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    session_date: date

    model_config = {"from_attributes": True}
