"""
Todo model — Smart To-Do List.
"""
import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Todo(Base):
    """
    Tabel todos — Daftar tugas kerja harian.
    Kategori: Penting (priority=important), Hari Ini (task_date=today), Besok (task_date=tomorrow).
    """
    __tablename__ = "todos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default="normal", comment="important | normal")
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="pending | done")
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    task_date: Mapped[date | None] = mapped_column(Date, comment="Tanggal tugas untuk filter")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="todos")

    def __repr__(self) -> str:
        return f"<Todo(title='{self.title}', status='{self.status}')>"
