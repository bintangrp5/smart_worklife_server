"""CRUD for Dashboard Home aggregation."""
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pomodoro import PomodoroSession
from app.models.todo import Todo
from app.models.health import HydrationLog, HydrationSetting


async def get_dashboard_summary(db: AsyncSession, user_id: uuid.UUID) -> dict:
    today = datetime.now(timezone.utc).date()

    # --- Pomodoro ---
    focus_result = await db.execute(
        select(func.coalesce(func.sum(PomodoroSession.actual_duration_seconds), 0)).where(
            and_(
                PomodoroSession.user_id == user_id,
                PomodoroSession.session_date == today,
                PomodoroSession.session_type == "focus",
                PomodoroSession.status == "completed",
            )
        )
    )
    focus_seconds = focus_result.scalar() or 0

    break_result = await db.execute(
        select(func.coalesce(func.sum(PomodoroSession.actual_duration_seconds), 0)).where(
            and_(
                PomodoroSession.user_id == user_id,
                PomodoroSession.session_date == today,
                PomodoroSession.session_type == "break",
                PomodoroSession.status == "completed",
            )
        )
    )
    break_seconds = break_result.scalar() or 0

    total_seconds = focus_seconds + break_seconds
    work_pct = round((focus_seconds / total_seconds) * 100, 1) if total_seconds > 0 else 0.0
    rest_pct = round((break_seconds / total_seconds) * 100, 1) if total_seconds > 0 else 0.0
    efficiency = round(min(work_pct, 100.0), 1)

    # --- Todos ---
    total_todos_res = await db.execute(
        select(func.count()).where(and_(Todo.user_id == user_id, Todo.task_date == today))
    )
    total_todos = total_todos_res.scalar() or 0

    done_todos_res = await db.execute(
        select(func.count()).where(
            and_(Todo.user_id == user_id, Todo.task_date == today, Todo.status == "done")
        )
    )
    done_todos = done_todos_res.scalar() or 0
    completion_rate = round((done_todos / total_todos) * 100, 1) if total_todos > 0 else 0.0

    # --- Hydration ---
    hydration_logs_res = await db.execute(
        select(func.coalesce(func.sum(HydrationLog.amount_ml), 0.0)).where(
            and_(HydrationLog.user_id == user_id, HydrationLog.log_date == today)
        )
    )
    consumed_ml = float(hydration_logs_res.scalar() or 0.0)

    setting_res = await db.execute(
        select(HydrationSetting.daily_target_ml).where(HydrationSetting.user_id == user_id)
    )
    target_ml = float(setting_res.scalar() or 2000.0)
    hydration_pct = round((consumed_ml / target_ml) * 100, 1) if target_ml > 0 else 0.0

    return {
        "date": today.isoformat(),
        "focus_time_seconds": focus_seconds,
        "break_time_seconds": break_seconds,
        "tasks": {
            "total": total_todos,
            "done": done_todos,
            "completion_rate": completion_rate,
        },
        "balance": {
            "work_percent": work_pct,
            "rest_percent": rest_pct,
            "efficiency_score": efficiency,
        },
        "hydration": {
            "consumed_ml": consumed_ml,
            "target_ml": target_ml,
            "progress_percent": hydration_pct,
        },
    }


async def get_todo_preview(db: AsyncSession, user_id: uuid.UUID) -> list[Todo]:
    today = datetime.now(timezone.utc).date()
    result = await db.execute(
        select(Todo).where(
            and_(Todo.user_id == user_id, Todo.status == "pending", Todo.task_date == today)
        ).order_by(Todo.priority.desc(), Todo.deadline.asc().nullslast()).limit(5)
    )
    return result.scalars().all()
