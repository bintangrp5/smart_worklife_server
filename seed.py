import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

from app.models import StretchingExercise

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)

async def seed_data():
    async with async_session() as session:
        # Check if already seeded
        from sqlalchemy import select
        result = await session.execute(select(StretchingExercise))
        existing = result.scalars().all()
        if existing:
            print("Database already seeded with stretching exercises.")
            return

        exercises = [
            StretchingExercise(
                name="Neck Tilt",
                description="Miringkan kepala ke kiri dan kanan secara bergantian",
                body_part="neck",
                default_reps=10,
                default_duration_seconds=30,
                sort_order=1
            ),
            StretchingExercise(
                name="Shoulder Shrug",
                description="Angkat bahu ke atas lalu lepaskan secara perlahan",
                body_part="shoulder",
                default_reps=10,
                default_duration_seconds=30,
                sort_order=2
            ),
            StretchingExercise(
                name="Upper Back Stretch",
                description="Tarik kedua tangan ke depan dan bulatkan punggung atas",
                body_part="back",
                default_reps=10,
                default_duration_seconds=30,
                sort_order=3
            ),
        ]
        session.add_all(exercises)
        await session.commit()
        print(f"Successfully seeded {len(exercises)} stretching exercises.")

if __name__ == "__main__":
    asyncio.run(seed_data())
