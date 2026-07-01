import uuid
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rating import AppRating
from app.schemas.rating import AppRatingCreate

async def create_or_update_rating(
    db: AsyncSession, user_id: uuid.UUID, data: AppRatingCreate
) -> AppRating:
    # Cek apakah user sudah pernah rating fitur ini
    result = await db.execute(
        select(AppRating).where(
            and_(AppRating.user_id == user_id, AppRating.feature_name == data.feature_name)
        )
    )
    existing_rating = result.scalar_one_or_none()

    if existing_rating:
        # Update existing
        existing_rating.rating = data.rating
        existing_rating.review = data.review
        await db.flush()
        await db.refresh(existing_rating)
        return existing_rating
    else:
        # Create new
        new_rating = AppRating(
            user_id=user_id,
            feature_name=data.feature_name,
            rating=data.rating,
            review=data.review
        )
        db.add(new_rating)
        await db.flush()
        await db.refresh(new_rating)
        return new_rating

async def get_user_ratings(db: AsyncSession, user_id: uuid.UUID) -> list[AppRating]:
    result = await db.execute(
        select(AppRating).where(AppRating.user_id == user_id)
    )
    return result.scalars().all()
