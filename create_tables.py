import asyncio
from app.database import init_db
from app.models import *

async def main():
    await init_db()
    print("Database tables created/updated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
