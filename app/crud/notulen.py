"""CRUD operations for Smart Notulen."""
import uuid
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notulen import Notulen
from app.schemas.notulen import NotulenSave


async def create_notulen(
    db: AsyncSession,
    user_id: uuid.UUID,
    transcript: str,
    duration_seconds: Optional[int],
    audio_url: Optional[str],
) -> Notulen:
    notulen = Notulen(
        user_id=user_id,
        title="Draft Notulen",
        transcript=transcript,
        duration_seconds=duration_seconds,
        audio_url=audio_url,
    )
    db.add(notulen)
    await db.flush()
    await db.refresh(notulen)
    return notulen


async def get_notulen(
    db: AsyncSession, notulen_id: uuid.UUID, user_id: uuid.UUID
) -> Optional[Notulen]:
    result = await db.execute(
        select(Notulen).where(
            and_(Notulen.id == notulen_id, Notulen.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def update_summary(
    db: AsyncSession, notulen: Notulen, summary: str, action_items: list[str]
) -> Notulen:
    notulen.summary = summary
    notulen.action_items = action_items
    await db.flush()
    await db.refresh(notulen)
    return notulen


async def save_notulen(
    db: AsyncSession, notulen: Notulen, data: NotulenSave
) -> Notulen:
    notulen.title = data.title
    if data.meeting_date:
        notulen.meeting_date = data.meeting_date
    await db.flush()
    await db.refresh(notulen)
    return notulen


async def list_notulens(db: AsyncSession, user_id: uuid.UUID) -> list[Notulen]:
    result = await db.execute(
        select(Notulen)
        .where(Notulen.user_id == user_id)
        .order_by(Notulen.created_at.desc())
    )
    return result.scalars().all()


async def delete_notulen(db: AsyncSession, notulen: Notulen) -> None:
    await db.delete(notulen)
    await db.flush()
