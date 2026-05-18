"""Router — Smart Stretching."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user_id
from app.crud import stretching as crud
from app.schemas.stretching import (
    StretchingExerciseResponse,
    StretchingSessionCreate,
    StretchingSessionResponse,
    StretchingRepCreate,
    StretchingRepResponse,
)

router = APIRouter(prefix="/stretching", tags=["Smart Stretching"])


@router.get("/exercises", response_model=list[StretchingExerciseResponse])
async def list_exercises(db: AsyncSession = Depends(get_db)):
    """Daftar master gerakan peregangan (tidak perlu auth)."""
    return await crud.get_exercises(db)


@router.post("/sessions", response_model=StretchingSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    data: StretchingSessionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await crud.create_session(db, user_id, data)


@router.post("/sessions/{session_id}/reps", response_model=StretchingRepResponse, status_code=status.HTTP_201_CREATED)
async def add_rep(
    session_id: uuid.UUID,
    data: StretchingRepCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    session = await crud.get_session(db, session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesi stretching tidak ditemukan.")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Sesi sudah selesai atau dibatalkan.")
    return await crud.add_rep(db, session, data)


@router.put("/sessions/{session_id}/complete", response_model=StretchingSessionResponse)
async def complete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    session = await crud.get_session(db, session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesi stretching tidak ditemukan.")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Sesi sudah selesai atau dibatalkan.")
    return await crud.complete_session(db, session)


@router.get("/sessions/history", response_model=list[StretchingSessionResponse])
async def session_history(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await crud.get_session_history(db, user_id)
