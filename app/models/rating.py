"""Model for App Ratings."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class AppRating(Base):
    __tablename__ = "app_ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    feature_name = Column(String(100), nullable=False)  # e.g. "Pomodoro", "Keseluruhan"
    rating = Column(Integer, nullable=False)             # 1–5
    review = Column(Text, nullable=True)                 # Komentar opsional
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        # Satu user hanya bisa rating satu kali per fitur
        UniqueConstraint("user_id", "feature_name", name="uq_user_feature_rating"),
    )
