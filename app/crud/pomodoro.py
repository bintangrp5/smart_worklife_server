"""CRUD operations for Smart Pomodoro."""
import uuid
from datetime import datetime, timezone, date
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pomodoro import PomodoroSetting, PomodoroSession
from app.schemas.pomodoro import PomodoroSettingUpdate, PomodoroSessionStart, PomodoroSessionEnd

DEFAULT_MODES = {
    "classic":   {"focus_duration_minutes": 25, "break_duration_minutes": 5},
    "deep_work": {"focus_duration_minutes": 50, "break_duration_minutes": 10},
    "extend":    {"focus_duration_minutes": 45, "break_duration_minutes": 15},
}


async def get_or_create_settings(db: AsyncSession, user_id: uuid.UUID) -> list[PomodoroSetting]:
    result = await db.execute(select(PomodoroSetting).where(PomodoroSetting.user_id == user_id))
    settings = result.scalars().all()

    if not settings:
        settings = [
            PomodoroSetting(user_id=user_id, mode=mode, **vals)
            for mode, vals in DEFAULT_MODES.items()
        ]
        db.add_all(settings)
        await db.flush()

    return settings


async def update_setting(
    db: AsyncSession, user_id: uuid.UUID, mode: str, data: PomodoroSettingUpdate
) -> Optional[PomodoroSetting]:
    result = await db.execute(
        select(PomodoroSetting).where(
            and_(PomodoroSetting.user_id == user_id, PomodoroSetting.mode == mode)
        )
    )
    setting = result.scalar_one_or_none()
    if not setting:
        return None
    setting.focus_duration_minutes = data.focus_duration_minutes
    setting.break_duration_minutes = data.break_duration_minutes
    await db.flush()
    await db.refresh(setting)
    return setting


async def start_session(
    db: AsyncSession, user_id: uuid.UUID, data: PomodoroSessionStart
) -> PomodoroSession:
    session = PomodoroSession(
        user_id=user_id,
        mode=data.mode,
        session_type=data.session_type,
        duration_seconds=data.duration_seconds,
        setting_id=data.setting_id,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
        session_date=datetime.now(timezone.utc).date(),
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


async def end_session(
    db: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID, data: PomodoroSessionEnd
) -> Optional[PomodoroSession]:
    result = await db.execute(
        select(PomodoroSession).where(
            and_(PomodoroSession.id == session_id, PomodoroSession.user_id == user_id)
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        return None
    session.status = data.status
    session.actual_duration_seconds = data.actual_duration_seconds
    session.ended_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(session)
    return session


async def get_today_sessions(db: AsyncSession, user_id: uuid.UUID) -> list[PomodoroSession]:
    today = datetime.now(timezone.utc).date()
    result = await db.execute(
        select(PomodoroSession).where(
            and_(PomodoroSession.user_id == user_id, PomodoroSession.session_date == today)
        ).order_by(PomodoroSession.started_at.desc())
    )
    return result.scalars().all()
