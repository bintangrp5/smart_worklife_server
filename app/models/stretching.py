"""
Stretching models — Exercise master data, session tracking, and rep details.
Supports MediaPipe-based pose detection with accuracy scoring.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Boolean, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class StretchingExercise(Base):
    """
    Tabel stretching_exercises — Master data gerakan peregangan.
    Data ini bersifat global (tidak per user), di-manage oleh admin.
    """
    __tablename__ = "stretching_exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(
        Text, comment="URL gambar panduan gerakan"
    )
    animation_url: Mapped[str | None] = mapped_column(
        Text, comment="URL animasi panduan gerakan"
    )
    default_reps: Mapped[int] = mapped_column(
        Integer, default=10, comment="Jumlah repetisi default"
    )
    default_duration_seconds: Mapped[int] = mapped_column(
        Integer, default=30, comment="Durasi default per gerakan (detik)"
    )
    body_part: Mapped[str | None] = mapped_column(
        String(50), comment="Area tubuh target (neck, back, shoulder, etc.)"
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    sessions: Mapped[list["StretchingSession"]] = relationship(
        back_populates="exercise", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<StretchingExercise(name='{self.name}', body_part='{self.body_part}')>"


class StretchingSession(Base):
    """
    Tabel stretching_sessions — Riwayat sesi stretching per user.
    Mencatat performa dan akurasi gerakan menggunakan MediaPipe.
    """
    __tablename__ = "stretching_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stretching_exercises.id", ondelete="CASCADE"),
        nullable=False
    )
    total_reps: Mapped[int] = mapped_column(Integer, default=0)
    correct_reps: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int | None] = mapped_column(
        Integer, comment="Durasi aktual sesi (detik)"
    )
    accuracy_score: Mapped[float | None] = mapped_column(
        Float, comment="Skor akurasi 0-100 berdasarkan correct_reps/total_reps"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="in_progress",
        comment="completed | cancelled | in_progress"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="stretching_sessions")
    exercise: Mapped["StretchingExercise"] = relationship(back_populates="sessions")
    reps: Mapped[list["StretchingRep"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<StretchingSession(accuracy={self.accuracy_score}, status='{self.status}')>"


class StretchingRep(Base):
    """
    Tabel stretching_reps — Detail setiap repetisi dalam sesi stretching.
    Mencatat apakah posisi benar dan feedback dari MediaPipe detection.
    """
    __tablename__ = "stretching_reps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stretching_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    rep_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str | None] = mapped_column(
        Text, comment="Pesan feedback posisi (e.g., 'Luruskan punggung')"
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    session: Mapped["StretchingSession"] = relationship(back_populates="reps")

    def __repr__(self) -> str:
        return f"<StretchingRep(rep={self.rep_number}, correct={self.is_correct})>"
