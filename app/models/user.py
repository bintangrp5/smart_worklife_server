"""
User and UserPreference models.
Handles authentication data and user settings.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class User(Base):
    """
    Tabel users — Data pengguna utama.
    Menyimpan informasi autentikasi dan profil dasar.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    full_name: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    
    # --- Auth & Verification ---
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    otp_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # --- Onboarding / Profile Fields ---
    gender: Mapped[str | None] = mapped_column(String(20))
    age: Mapped[int | None] = mapped_column(Integer)
    industry: Mapped[str | None] = mapped_column(String(100))
    work_start_time: Mapped[str | None] = mapped_column(String(10)) # Format "HH:mm"
    work_end_time: Mapped[str | None] = mapped_column(String(10))   # Format "HH:mm"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    preference: Mapped["UserPreference"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    pomodoro_settings: Mapped[list["PomodoroSetting"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    pomodoro_sessions: Mapped[list["PomodoroSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    stretching_sessions: Mapped[list["StretchingSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    bmi_profile: Mapped["BMIProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    hydration_setting: Mapped["HydrationSetting"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    hydration_logs: Mapped[list["HydrationLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    todos: Mapped[list["Todo"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notulens: Mapped[list["Notulen"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"


class UserPreference(Base):
    """
    Tabel user_preferences — Preferensi pengguna.
    Relasi 1-to-1 dengan User.
    """
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    theme: Mapped[str] = mapped_column(String(20), default="light")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    language: Mapped[str] = mapped_column(String(10), default="id")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="preference")

    def __repr__(self) -> str:
        return f"<UserPreference(user_id={self.user_id}, theme='{self.theme}')>"
