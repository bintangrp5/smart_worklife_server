from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.database import async_session
from app.models.user import User

async def clean_pending_deletions():
    async with async_session() as session:
        try:
            # Cari user yang masa tenggangnya sudah habis (14 hari)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=14)
            result = await session.execute(
                select(User).where(User.deletion_scheduled_at <= cutoff_date)
            )
            users_to_delete = result.scalars().all()
            for user in users_to_delete:
                print(f"[CLEANUP] Deleting user {user.email} permanently...")
                await session.delete(user)
            if users_to_delete:
                await session.commit()
                print(f"[CLEANUP] Cleaned {len(users_to_delete)} accounts.")
        except Exception as e:
            await session.rollback()
            print(f"[CLEANUP ERROR] Failed to clean pending deletions: {e}")
