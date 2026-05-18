"""Router — Smart Pomodoro."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user_id
from app.crud import pomodoro as crud
from app.schemas.pomodoro import (
    PomodoroSettingResponse,
    PomodoroSettingUpdate,
    PomodoroSessionStart,
    PomodoroSessionEnd,
    PomodoroSessionResponse,
)

router = APIRouter(prefix="/pomodoro", tags=["Smart Pomodoro"])


@router.get("/settings", response_model=list[PomodoroSettingResponse])
async def get_settings(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Ambil pengaturan semua mode. Otomatis dibuat jika belum ada."""
    return await crud.get_or_create_settings(db, user_id)


@router.put("/settings/{mode}", response_model=PomodoroSettingResponse)
async def update_setting(
    mode: str,
    data: PomodoroSettingUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    if mode not in ("classic", "deep_work", "extend"):
        raise HTTPException(status_code=400, detail="Mode tidak valid. Gunakan: classic, deep_work, extend.")
    setting = await crud.update_setting(db, user_id, mode, data)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting tidak ditemukan.")
    return setting


@router.post("/sessions/start", response_model=PomodoroSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    data: PomodoroSessionStart,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await crud.start_session(db, user_id, data)


@router.put("/sessions/{session_id}/end", response_model=PomodoroSessionResponse)
async def end_session(
    session_id: uuid.UUID,
    data: PomodoroSessionEnd,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    session = await crud.end_session(db, session_id, user_id, data)
    if not session:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan.")
    return session


@router.get("/sessions/today", response_model=list[PomodoroSessionResponse])
async def today_sessions(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await crud.get_today_sessions(db, user_id)
