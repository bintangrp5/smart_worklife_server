"""
Smart-WorkLife API — main entrypoint.
FastAPI + SQLAlchemy Async + PostgreSQL (Neon)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.models import *  # noqa: F401, F403 — populate SQLAlchemy metadata

# Routers
from app.routers import auth, todo, pomodoro, health, stretching, notulen, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Smart-WorkLife API",
    description=(
        "Backend API untuk aplikasi **Smart-WorkLife** — asisten produktivitas "
        "dan kesehatan bagi pekerja kantoran.\n\n"
        "**Autentikasi:** Gunakan `/auth/register` dan `/auth/login` untuk mendapatkan JWT Token. "
        "Sertakan token pada header `Authorization: Bearer <TOKEN>`."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain Flutter/mobile saat production
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