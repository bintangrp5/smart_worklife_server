import asyncio
from sqlalchemy import text
from app.database import engine

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text('SELECT count(*) FROM app_ratings'))
        print('COUNT:', res.scalar())

if __name__ == '__main__':
    asyncio.run(check())
