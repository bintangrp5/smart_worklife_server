"""
Notulen model — Smart Meeting Notes with AI Summary.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Notulen(Base):
    """
    Tabel notulens — Notulen rapat.
    Menyimpan transkripsi audio (Speech-to-Text) dan ringkasan AI.
    """
    __tablename__ = "notulens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    transcript: Mapped[str | None] = mapped_column(Text, comment="Hasil transkripsi audio")
    summary: Mapped[str | None] = mapped_column(Text, comment="Ringkasan AI")
    action_items: Mapped[dict | None] = mapped_column(JSONB, comment="Action items dari AI")
    duration_seconds: Mapped[int | None] = mapped_column(Integer, comment="Durasi rekaman (detik)")
    audio_url: Mapped[str | None] = mapped_column(Text, comment="URL file audio")
    meeting_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="notulens")

    def __repr__(self) -> str:
        return f"<Notulen(title='{self.title}')>"
