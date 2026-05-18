"""
Dev helper: Ambil OTP dari database untuk testing.
Run: python dev_get_otp.py bintang2@example.com
"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
email = sys.argv[1] if len(sys.argv) > 1 else "bintang2@example.com"


async def get_otp():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT email, otp_code, otp_expires_at, is_verified FROM users WHERE email = :email"),
            {"email": email}
        )
        row = result.fetchone()
        if row:
            print(f"\nEmail      : {row[0]}")
            print(f"OTP Code   : {row[1]}")
            print(f"OTP Expires: {row[2]}")
            print(f"Verified   : {row[3]}\n")
        else:
            print(f"User dengan email '{email}' tidak ditemukan.")
    await engine.dispose()


asyncio.run(get_otp())
