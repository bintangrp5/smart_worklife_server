import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, *, full_name: str, email: str, password: str) -> User:
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        is_verified=False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_google_user(db: AsyncSession, *, email: str, full_name: str, google_id: str, avatar_url: str) -> User:
    db_user = User(
        email=email,
        full_name=full_name,
        google_id=google_id,
        avatar_url=avatar_url,
        is_verified=True,  # Google accounts are pre-verified
        hashed_password=None
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=4))


async def update_user_otp(db: AsyncSession, user: User) -> str:
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=1)
    await db.commit()
    await db.refresh(user)
    return otp
