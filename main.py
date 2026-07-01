import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models import *  # noqa: F401, F403 — populate SQLAlchemy metadata

# Routers
from app.routers import auth, todo, pomodoro, health, stretching, notulen, dashboard, chat, berita, rating, admin

# Buat folder uploads hanya jika berjalan di local (bukan Vercel)
if not os.getenv("VERCEL"):
    os.makedirs("uploads/avatars", exist_ok=True)


app = FastAPI(
    title="Smart-WorkLife API",
    description=(
        "Backend API untuk aplikasi **Smart-WorkLife** — asisten produktivitas "
        "dan kesehatan bagi pekerja kantoran.\n\n"
        "**Autentikasi:** Gunakan `/auth/register` dan `/auth/login` untuk mendapatkan JWT Token. "
        "Sertakan token pada header `Authorization: Bearer <TOKEN>`."
    ),
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain spesifik saat production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ──────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# ── Routers ───────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth.router,        prefix=PREFIX)
app.include_router(todo.router,        prefix=PREFIX)
app.include_router(pomodoro.router,    prefix=PREFIX)
app.include_router(health.router,      prefix=PREFIX)
app.include_router(stretching.router,  prefix=PREFIX)
app.include_router(notulen.router,     prefix=PREFIX)
app.include_router(dashboard.router,   prefix=PREFIX)
app.include_router(chat.router,        prefix=PREFIX)
app.include_router(berita.router,      prefix=PREFIX)
app.include_router(rating.router,      prefix=PREFIX)
app.include_router(admin.router)

# Static files (uploads lokal, logo frontend)
from fastapi.staticfiles import StaticFiles

if not os.getenv("VERCEL") and os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount /static agar logo dan asset frontend bisa diakses
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount /admin_assets untuk melayani file statis React (Vite Build)
if os.path.exists("admin_dist"):
    app.mount("/admin_assets", StaticFiles(directory="admin_dist"), name="admin_assets")


# ── Cron Endpoint (pengganti background task) ─────────────────────────
# Endpoint ini dipanggil otomatis setiap jam oleh Vercel Cron Job
# (lihat konfigurasi "crons" di vercel.json)
@app.get("/api/v1/cron/cleanup-pending-deletions", tags=["Cron Jobs"])
async def cron_cleanup():
    """
    Membersihkan akun yang telah melewati masa Pending Deletion 14 hari.
    Dipanggil otomatis oleh Vercel Cron Job setiap jam (lihat vercel.json).
    """
    from app.tasks.account_cleanup import clean_pending_deletions
    await clean_pending_deletions()
    return {"status": "ok", "message": "Cleanup selesai dijalankan."}


# ── Root & Health Check ───────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "app": "Smart-WorkLife API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running 🚀",
    }


@app.get("/health", tags=["Root"])
def health_check():
    return {"status": "healthy"}