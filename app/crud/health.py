"""CRUD operations for Smart Health — BMI & Hydration."""
import uuid
from datetime import datetime, timezone, date
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health import BMIProfile, HydrationSetting, HydrationLog
from app.schemas.health import BMIInput, HydrationSettingUpdate, HydrationLogCreate


# --- BMI ---
async def get_bmi(db: AsyncSession, user_id: uuid.UUID) -> Optional[BMIProfile]:
    result = await db.execute(select(BMIProfile).where(BMIProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def upsert_bmi(db: AsyncSession, user_id: uuid.UUID, data: BMIInput) -> BMIProfile:
    profile = await get_bmi(db, user_id)
    if not profile:
        profile = BMIProfile(user_id=user_id, height_cm=data.height_cm, weight_kg=data.weight_kg)
        db.add(profile)
    else:
        profile.height_cm = data.height_cm
        profile.weight_kg = data.weight_kg

    profile.calculate_bmi()
    await db.flush()
    await db.refresh(profile)

    # Update hydration target setelah BMI diperbarui
    await _sync_hydration_target(db, user_id, data.weight_kg)
    return profile


async def _sync_hydration_target(db: AsyncSession, user_id: uuid.UUID, weight_kg: float):
    """Sinkronisasi target hidrasi berdasarkan berat badan terbaru."""
    result = await db.execute(select(HydrationSetting).where(HydrationSetting.user_id == user_id))
    setting = result.scalar_one_or_none()
    target = round(weight_kg * 30, 1)
    if not setting:
        setting = HydrationSetting(user_id=user_id, daily_target_ml=target)
        db.add(setting)
    else:
        setting.daily_target_ml = target
    await db.flush()


# --- Hydration Settings ---
async def get_hydration_setting(db: AsyncSession, user_id: uuid.UUID) -> Optional[HydrationSetting]:
    result = await db.execute(select(HydrationSetting).where(HydrationSetting.user_id == user_id))
    return result.scalar_one_or_none()


async def update_hydration_setting(
    db: AsyncSession, user_id: uuid.UUID, data: HydrationSettingUpdate
) -> Optional[HydrationSetting]:
    setting = await get_hydration_setting(db, user_id)
    if not setting:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(setting, field, value)
    await db.flush()
    await db.refresh(setting)
    return setting


# --- Hydration Log ---
async def add_hydration_log(
    db: AsyncSession, user_id: uuid.UUID, data: HydrationLogCreate
) -> HydrationLog:
    log = HydrationLog(
        user_id=user_id,
        amount_ml=data.amount_ml,
        log_date=datetime.now(timezone.utc).date(),
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def get_today_hydration(db: AsyncSession, user_id: uuid.UUID):
    today = datetime.now(timezone.utc).date()

    logs_result = await db.execute(
        select(HydrationLog).where(
            and_(HydrationLog.user_id == user_id, HydrationLog.log_date == today)
        ).order_by(HydrationLog.logged_at.desc())
    )
    logs = logs_result.scalars().all()
    consumed = sum(l.amount_ml for l in logs)

    setting = await get_hydration_setting(db, user_id)
    target = setting.daily_target_ml if setting else 2000.0
    progress = round((consumed / target) * 100, 1) if target > 0 else 0.0

    return {"log_date": today, "consumed_ml": consumed, "target_ml": target, "progress_percent": progress, "logs": logs}


async def delete_hydration_log(
    db: AsyncSession, log_id: uuid.UUID, user_id: uuid.UUID
) -> Optional[HydrationLog]:
    result = await db.execute(
        select(HydrationLog).where(and_(HydrationLog.id == log_id, HydrationLog.user_id == user_id))
    )
    log = result.scalar_one_or_none()
    if log:
        await db.delete(log)
        await db.flush()
    return log
