"""Schemas for Smart Health (BMI + Hydration)."""
import uuid
from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, Field


# --- BMI ---
class BMIInput(BaseModel):
    height_cm: float = Field(..., gt=50, lt=300, examples=[170.0])
    weight_kg: float = Field(..., gt=10, lt=500, examples=[65.0])


class BMIResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    height_cm: float
    weight_kg: float
    bmi_value: Optional[float]
    bmi_category: Optional[str]
    calculated_at: Optional[datetime]
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Hydration Settings ---
class HydrationSettingUpdate(BaseModel):
    reminder_interval_minutes: Optional[int] = Field(None, ge=15, le=480)
    reminder_enabled: Optional[bool] = None
    reminder_start_time: Optional[time] = None
    reminder_end_time: Optional[time] = None


class HydrationSettingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    daily_target_ml: float
    reminder_interval_minutes: int
    reminder_enabled: bool
    reminder_start_time: time
    reminder_end_time: time
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Hydration Log ---
class HydrationLogCreate(BaseModel):
    amount_ml: float = Field(..., gt=0, le=2000, examples=[250.0])


class HydrationLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    amount_ml: float
    log_date: date
    logged_at: datetime

    model_config = {"from_attributes": True}


class HydrationTodayResponse(BaseModel):
    log_date: date
    consumed_ml: float
    target_ml: float
    progress_percent: float
    logs: list[HydrationLogResponse]
