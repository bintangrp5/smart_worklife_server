"""
Migration script: Add missing auth columns to users table.
Run once: python migrate_add_auth_columns.py
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

# SQL: Add columns only if they don't exist yet
MIGRATION_SQL = """
DO $$
BEGIN
    -- is_verified
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='is_verified'
    ) THEN
        ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE;
        RAISE NOTICE 'Added column: is_verified';
    ELSE
        RAISE NOTICE 'Column already exists: is_verified';
    END IF;

    -- otp_code
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='otp_code'
    ) THEN
        ALTER TABLE users ADD COLUMN otp_code VARCHAR(6);
        RAISE NOTICE 'Added column: otp_code';
    ELSE
        RAISE NOTICE 'Column already exists: otp_code';
    END IF;

    -- otp_expires_at
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='otp_expires_at'
    ) THEN
        ALTER TABLE users ADD COLUMN otp_expires_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column: otp_expires_at';
    ELSE
        RAISE NOTICE 'Column already exists: otp_expires_at';
    END IF;

    -- google_id
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='google_id'
    ) THEN
        ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;
        RAISE NOTICE 'Added column: google_id';
    ELSE
        RAISE NOTICE 'Column already exists: google_id';
    END IF;

END $$;
"""


async def run_migration():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        print("Connecting to database...")
        await conn.execute(text(MIGRATION_SQL))
        print("Migration complete! All auth columns are now present.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migration())
