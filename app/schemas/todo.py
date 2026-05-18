"""Schemas for Smart To-Do List."""
import uuid
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, examples=["Review proposal"])
    description: Optional[str] = None
    priority: str = Field(default="normal", pattern="^(important|normal)$")
    deadline: Optional[datetime] = None
    task_date: Optional[date] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(important|normal)$")
    status: Optional[str] = Field(None, pattern="^(pending|done)$")
    deadline: Optional[datetime] = None
    task_date: Optional[date] = None


class TodoResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    priority: str
    status: str
    deadline: Optional[datetime]
    task_date: Optional[date]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
