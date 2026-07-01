"""
Migration: Fix users table schema mismatch.
- Renames 'username' column to 'full_name' (or makes it nullable if full_name already exists)
- Run once: python migrate_fix_users_schema.py
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
    -- Cek apakah kolom 'username' ada
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='username'
    ) THEN
        -- Cek apakah 'full_name' sudah ada
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='users' AND column_name='full_name'
        ) THEN
            -- Keduanya ada: salin data username -> full_name lalu drop username
            UPDATE users SET full_name = username WHERE full_name IS NULL;
            ALTER TABLE users DROP COLUMN username;
            RAISE NOTICE 'Migrated username -> full_name and dropped username column';
        ELSE
            -- Hanya username yang ada: rename ke full_name
            ALTER TABLE users RENAME COLUMN username TO full_name;
            -- Ubah jadi nullable (model pakai nullable=True)
            ALTER TABLE users ALTER COLUMN full_name DROP NOT NULL;
            RAISE NOTICE 'Renamed username -> full_name and made nullable';
        END IF;
    ELSE
        RAISE NOTICE 'Column username does not exist, nothing to migrate';
    END IF;

    -- Pastikan full_name nullable
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='full_name'
    ) THEN
        ALTER TABLE users ALTER COLUMN full_name DROP NOT NULL;
        RAISE NOTICE 'Ensured full_name is nullable';
    END IF;

END $$;
"""


async def run_migration():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        print("Connecting to database...")
        await conn.execute(text(MIGRATION_SQL))
        print("Migration complete! users table schema is now correct.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migration())
