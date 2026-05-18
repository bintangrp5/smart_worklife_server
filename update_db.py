import asyncio
from sqlalchemy import text
from app.database import async_session

async def update_schema():
    async with async_session() as session:
        print("Updating users table schema...")
        # Tambahkan kolom baru ke tabel users
        commands = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(20)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS age INTEGER",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS industry VARCHAR(100)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS work_start_time VARCHAR(10)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS work_end_time VARCHAR(10)"
        ]
        
        for cmd in commands:
            try:
                await session.execute(text(cmd))
                print(f"Executed: {cmd}")
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
        
        await session.commit()
        print("Schema update completed!")

if __name__ == "__main__":
    asyncio.run(update_schema())
