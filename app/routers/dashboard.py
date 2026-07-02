"""Router — Dashboard Home aggregation."""
import uuid

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user_id
from app.crud import dashboard as crud
from app.schemas.todo import TodoResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_summary(
    target_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Satu endpoint yang mengambil semua metrik harian untuk Home Screen:
    - Focus Time & Break Time (dari Pomodoro)
    - Task completion rate (dari To-Do)
    - Today's Balance (work vs rest %)
    - Hydration progress
    """
    return await crud.get_dashboard_summary(db, user_id, target_date)


@router.get("/todos/preview", response_model=list[TodoResponse])
async def todo_preview(
    target_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Preview 5 tugas pending hari ini untuk widget di Home Screen."""
    return await crud.get_todo_preview(db, user_id, target_date)


@router.get("/leaderboard")
async def get_leaderboard(
    target_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Get leaderboard of all users ranked by points for a specific date (defaults to today).
    """
    return await crud.get_leaderboard(db, target_date)
