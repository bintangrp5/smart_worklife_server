"""
Migration script: Add deletion_scheduled_at column to users table.
Run once: python migrate_deletion_scheduled.py
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/smartworklife"
)

MIGRATION_SQL = """
DO $$
BEGIN
    -- deletion_scheduled_at
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='deletion_scheduled_at'
    ) THEN
        ALTER TABLE users ADD COLUMN deletion_scheduled_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column: deletion_scheduled_at';
    ELSE
        RAISE NOTICE 'Column already exists: deletion_scheduled_at';
    END IF;
END $$;
"""


async def run_migration():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        print("Connecting to database...")
        await conn.execute(text(MIGRATION_SQL))
        print("Migration complete! deletion_scheduled_at column is now present.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migration())
