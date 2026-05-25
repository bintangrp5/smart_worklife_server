import asyncio
from sqlalchemy import text
from app.database import async_session, engine
from app.core.security import create_access_token

async def get_token():
    async with async_session() as session:
        result = await session.execute(text("SELECT id, email, full_name FROM users LIMIT 5"))
        users = result.all()
        if not users:
            print("No users found in database. Please register a user first!")
            return
        
        print("Existing users in database:")
        for u in users:
            token = create_access_token(subject=str(u[0]))
            print(f"- Name: {u[2]} | Email: {u[1]}")
            print(f"  Token: {token}\n")

async def main():
    try:
        await get_token()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
