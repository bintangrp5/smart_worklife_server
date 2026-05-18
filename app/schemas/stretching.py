"""Schemas for Smart Stretching."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StretchingExerciseResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    image_url: Optional[str]
    animation_url: Optional[str]
    default_reps: int
    default_duration_seconds: int
    body_part: Optional[str]
    sort_order: int

    model_config = {"from_attributes": True}


class StretchingSessionCreate(BaseModel):
    exercise_id: uuid.UUID


class StretchingRepCreate(BaseModel):
    rep_number: int = Field(..., ge=1)
    is_correct: bool
    feedback: Optional[str] = None


class StretchingRepResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    rep_number: int
    is_correct: bool
    feedback: Optional[str]
    recorded_at: datetime

    model_config = {"from_attributes": True}


class StretchingSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    exercise_id: uuid.UUID
    total_reps: int
    correct_reps: int
    duration_seconds: Optional[int]
    accuracy_score: Optional[float]
    status: str
    started_at: datetime
    ended_at: Optional[datetime]

    model_config = {"from_attributes": True}
