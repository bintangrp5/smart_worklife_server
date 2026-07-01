from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class AppRatingCreate(BaseModel):
    feature_name: str = Field(..., description="Nama fitur (contoh: Keseluruhan Aplikasi, Pomodoro, dll)")
    rating: int = Field(..., ge=1, le=5, description="Nilai rating 1 sampai 5")
    review: Optional[str] = Field(None, description="Komentar ulasan (opsional)")

class AppRatingResponse(BaseModel):
    id: UUID
    user_id: UUID
    feature_name: str
    rating: int
    review: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
