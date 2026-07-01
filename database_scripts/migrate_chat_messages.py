import asyncio
from sqlalchemy import text
from app.database import async_session, engine

async def update_schema():
    async with async_session() as session:
        print("Updating chat_messages table schema...")
        commands = [
            "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS deleted_for_everyone BOOLEAN DEFAULT FALSE",
            "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS deleted_by_sender BOOLEAN DEFAULT FALSE",
            "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS deleted_by_receiver BOOLEAN DEFAULT FALSE"
        ]
        
        for cmd in commands:
            try:
                await session.execute(text(cmd))
                print(f"Executed: {cmd}")
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
        
        await session.commit()
        print("Schema update completed!")

async def main():
    try:
        await update_schema()
    finally:
        await engine.dispose()
        print("Engine disposed.")

if __name__ == "__main__":
    asyncio.run(main())
