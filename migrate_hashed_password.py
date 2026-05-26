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
    -- Pastikan hashed_password bisa bernilai NULL (untuk Google Sign-In)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='hashed_password'
    ) THEN
        ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;
        RAISE NOTICE 'Altered hashed_password to DROP NOT NULL';
    END IF;
END $$;
"""

async def run_migration():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        print("Connecting to database...")
        await conn.execute(text(MIGRATION_SQL))
        print("Migration complete! users table hashed_password is now nullable.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
