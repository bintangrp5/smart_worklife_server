from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
import os
import urllib.parse
from datetime import datetime

router = APIRouter(
    prefix="/berita",
    tags=["Berita"]
)

# Ambil credential dari .env
MONGO_USER = os.getenv("MONGO_USER", "")
MONGO_PASS = os.getenv("MONGO_PASS", "")
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", "")
MONGO_DB_NAME = os.getenv("MONGO_DB", "Capstone")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "Data_Detik")
MONGO_COLLECTION_YT = os.getenv("MONGO_COLLECTION_YT", "Data_Youtube_2")

# Encode password yang memiliki special karakter seperti % atau @
encoded_pass = urllib.parse.quote_plus(MONGO_PASS) if MONGO_PASS else ""
if MONGO_USER and encoded_pass and MONGO_CLUSTER:
    MONGO_URI = f"mongodb+srv://{MONGO_USER}:{encoded_pass}@{MONGO_CLUSTER}/?retryWrites=true&w=majority"
else:
    # Fallback local
    MONGO_URI = "mongodb://localhost:27017"

# Inisialisasi Motor Client
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection_detik = db[MONGO_COLLECTION_NAME]
collection_yt = db[MONGO_COLLECTION_YT]

def format_date_indo(date_str):
    if not date_str: return ""
    try:
        clean_str = str(date_str).replace("Z", "")
        if "." in clean_str: clean_str = clean_str.split(".")[0]
        dt = datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            dt = datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return date_str
            
    hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    bulan_list = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
    return f"{hari_list[dt.weekday()]}, {dt.day} {bulan_list[dt.month - 1]} {dt.year} {dt.strftime('%H:%M')} WIB"

def format_detik(item):
    item["source"] = "Detik"
    return item

def format_yt(item):
    item["source"] = "YouTube"
    if "published_at" in item:
        item["published_date"] = format_date_indo(item["published_at"])
    if "video_id" in item:
        item["link"] = f"https://www.youtube.com/watch?v={item['video_id']}"
    return item

@router.get("/")
async def get_berita(limit: int = 100):
    """
    Mengambil data berita dari MongoDB secara asinkron.
    """
    try:
        # Fetch dari detik
        cursor_d = collection_detik.find({}, {"_id": 0}).sort("scraped_at", -1).limit(limit)
        data_d = await cursor_d.to_list(length=limit)
        
        # Fetch dari YT
        cursor_yt = collection_yt.find({}, {"_id": 0}).sort("scraped_at", -1).limit(limit)
        data_yt = await cursor_yt.to_list(length=limit)
        
        # Format dan gabung
        formatted_data = [format_detik(x) for x in data_d] + [format_yt(x) for x in data_yt]
        
        # Urutkan secara keseluruhan berdasarkan scraped_at
        formatted_data.sort(key=lambda x: str(x.get("scraped_at", "")), reverse=True)
        
        # Terapkan format cantik setelah sorting
        for item in formatted_data:
            if "scraped_at" in item:
                item["scraped_at"] = format_date_indo(item["scraped_at"])
                
        return formatted_data[:limit*2]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{keyword}")
async def get_by_keyword(keyword: str, limit: int = 100):
    """
    Mengambil data berdasarkan keyword.
    Menggunakan regex pada 'judul' atau match pada field 'keyword'.
    """
    try:
        query = {
            "$or": [
                {"keyword": keyword},
                {"title": {"$regex": keyword, "$options": "i"}}
            ]
        }
        
        cursor_d = collection_detik.find(query, {"_id": 0}).sort("scraped_at", -1).limit(limit)
        data_d = await cursor_d.to_list(length=limit)
        
        cursor_yt = collection_yt.find(query, {"_id": 0}).sort("scraped_at", -1).limit(limit)
        data_yt = await cursor_yt.to_list(length=limit)
        
        formatted_data = [format_detik(x) for x in data_d] + [format_yt(x) for x in data_yt]
        formatted_data.sort(key=lambda x: str(x.get("scraped_at", "")), reverse=True)
        
        for item in formatted_data:
            if "scraped_at" in item:
                item["scraped_at"] = format_date_indo(item["scraped_at"])
                
        return formatted_data[:limit*2]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
