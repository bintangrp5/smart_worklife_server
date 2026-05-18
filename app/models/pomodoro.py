"""
Pomodoro models — Settings and Session tracking.
Supports Classic (25/5), Deep Work (50/10), and Extend (custom) modes.
"""
import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class PomodoroSetting(Base):
    """
    Tabel pomodoro_settings — Pengaturan mode Pomodoro per user.
    Setiap user bisa punya beberapa setting (1 per mode).
    """
    __tablename__ = "pomodoro_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    mode: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="classic | deep_work | extend"
    )
    focus_duration_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Durasi fokus dalam menit"
    )
    break_duration_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Durasi istirahat dalam menit"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="pomodoro_settings")
    sessions: Mapped[list["PomodoroSession"]] = relationship(
        back_populates="setting", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PomodoroSetting(mode='{self.mode}', focus={self.focus_duration_minutes}min)>"


class PomodoroSession(Base):
    """
    Tabel pomodoro_sessions — Riwayat setiap sesi Pomodoro.
    Mencatat sesi fokus dan istirahat untuk dashboard metrics.
    """
    __tablename__ = "pomodoro_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    setting_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pomodoro_settings.id", ondelete="SET NULL"),
        nullable=True
    )
    mode: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Mode saat sesi berjalan"
    )
    session_type: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="focus | break"
    )
    duration_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Durasi yang di-set (detik)"
    )
    actual_duration_seconds: Mapped[int | None] = mapped_column(
        Integer, comment="Durasi aktual (detik)"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="in_progress",
        comment="completed | cancelled | in_progress"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    session_date: Mapped[date] = mapped_column(
        Date, nullable=False, default=lambda: datetime.now(timezone.utc).date(),
        comment="Tanggal sesi untuk agregasi harian"
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="pomodoro_sessions")
    setting: Mapped["PomodoroSetting | None"] = relationship(back_populates="sessions")

    def __repr__(self) -> str:
        return f"<PomodoroSession(type='{self.session_type}', status='{self.status}')>"
