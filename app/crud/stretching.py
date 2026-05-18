"""CRUD operations for Smart Stretching."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stretching import StretchingExercise, StretchingSession, StretchingRep
from app.schemas.stretching import StretchingSessionCreate, StretchingRepCreate


async def get_exercises(db: AsyncSession) -> list[StretchingExercise]:
    result = await db.execute(
        select(StretchingExercise)
        .where(StretchingExercise.is_active == True)
        .order_by(StretchingExercise.sort_order)
    )
    return result.scalars().all()


async def create_session(
    db: AsyncSession, user_id: uuid.UUID, data: StretchingSessionCreate
) -> StretchingSession:
    session = StretchingSession(
        user_id=user_id,
        exercise_id=data.exercise_id,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


async def get_session(
    db: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID
) -> Optional[StretchingSession]:
    result = await db.execute(
        select(StretchingSession).where(
            and_(StretchingSession.id == session_id, StretchingSession.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def add_rep(
    db: AsyncSession, session: StretchingSession, data: StretchingRepCreate
) -> StretchingRep:
    rep = StretchingRep(
        session_id=session.id,
        rep_number=data.rep_number,
        is_correct=data.is_correct,
        feedback=data.feedback,
    )
    db.add(rep)

    # Update counter di sesi
    session.total_reps = (session.total_reps or 0) + 1
    if data.is_correct:
        session.correct_reps = (session.correct_reps or 0) + 1

    await db.flush()
    await db.refresh(rep)
    return rep


async def complete_session(
    db: AsyncSession, session: StretchingSession
) -> StretchingSession:
    now = datetime.now(timezone.utc)
    session.status = "completed"
    session.ended_at = now
    session.duration_seconds = int((now - session.started_at).total_seconds())

    total = session.total_reps or 0
    correct = session.correct_reps or 0
    session.accuracy_score = round((correct / total) * 100, 1) if total > 0 else 0.0

    await db.flush()
    await db.refresh(session)
    return session


async def get_session_history(
    db: AsyncSession, user_id: uuid.UUID
) -> list[StretchingSession]:
    result = await db.execute(
        select(StretchingSession)
        .where(StretchingSession.user_id == user_id)
        .order_by(StretchingSession.started_at.desc())
    )
    return result.scalars().all()
