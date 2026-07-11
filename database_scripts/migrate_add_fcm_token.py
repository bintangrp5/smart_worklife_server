import os
import sys
import asyncio
import psycopg2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

def migrate():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is not set")
        return
        
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    db_url = db_url.replace("ssl=require", "sslmode=require")
    print(f"Connecting to {db_url}")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    try:
        print("Adding fcm_token to users table...")
        cur.execute("ALTER TABLE users ADD COLUMN fcm_token VARCHAR(255);")
        conn.commit()
        print("Successfully added fcm_token column.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
