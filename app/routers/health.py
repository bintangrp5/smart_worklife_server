"""Router — Smart Health (BMI + Hydration)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user_id
from app.crud import health as crud
from app.schemas.health import (
    BMIInput,
    BMIResponse,
    HydrationSettingUpdate,
    HydrationSettingResponse,
    HydrationLogCreate,
    HydrationLogResponse,
    HydrationTodayResponse,
)

router = APIRouter(prefix="/health", tags=["Smart Health"])


# ── BMI ──────────────────────────────────────────────────────────────
@router.get("/bmi", response_model=BMIResponse)
async def get_bmi(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    profile = await crud.get_bmi(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profil BMI belum diisi.")
    return profile


@router.post("/bmi", response_model=BMIResponse, status_code=status.HTTP_201_CREATED)
async def create_bmi(
    data: BMIInput,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Input pertama tinggi & berat badan. Auto-hitung BMI dan target air minum."""
    return await crud.upsert_bmi(db, user_id, data)


@router.put("/bmi", response_model=BMIResponse)
async def update_bmi(
    data: BMIInput,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Update tinggi & berat badan. Auto-hitung ulang BMI dan target air minum."""
    return await crud.upsert_bmi(db, user_id, data)


# ── Hydration Settings ────────────────────────────────────────────────
@router.get("/hydration/settings", response_model=HydrationSettingResponse)
async def get_hydration_settings(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    setting = await crud.get_hydration_setting(db, user_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Pengaturan hidrasi belum tersedia. Isi profil BMI terlebih dahulu.")
    return setting


@router.put("/hydration/settings", response_model=HydrationSettingResponse)
async def update_hydration_settings(
    data: HydrationSettingUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    setting = await crud.update_hydration_setting(db, user_id, data)
    if not setting:
        raise HTTPException(status_code=404, detail="Pengaturan hidrasi tidak ditemukan.")
    return setting


# ── Hydration Logs ────────────────────────────────────────────────────
@router.post("/hydration/logs", response_model=HydrationLogResponse, status_code=status.HTTP_201_CREATED)
async def add_water_log(
    data: HydrationLogCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await crud.add_hydration_log(db, user_id, data)


@router.get("/hydration/today", response_model=HydrationTodayResponse)
async def get_hydration_today(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await crud.get_today_hydration(db, user_id)


@router.delete("/hydration/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_water_log(
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    log = await crud.delete_hydration_log(db, log_id, user_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log minum tidak ditemukan.")
