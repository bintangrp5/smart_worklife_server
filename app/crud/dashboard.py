"""CRUD for Dashboard Home aggregation."""
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pomodoro import PomodoroSession
from app.models.todo import Todo
from app.models.health import HydrationLog, HydrationSetting
from app.models.stretching import StretchingSession


async def get_dashboard_summary(db: AsyncSession, user_id: uuid.UUID) -> dict:
    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

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

    # --- Stretching ---
    stretching_res = await db.execute(
        select(func.count(func.distinct(StretchingSession.exercise_id))).where(
            and_(
                StretchingSession.user_id == user_id,
                StretchingSession.status == "completed",
                StretchingSession.started_at >= today_start,
                StretchingSession.started_at <= today_end,
            )
        )
    )
    unique_stretching_count = int(stretching_res.scalar() or 0)
    stretching_count = min(unique_stretching_count, 6)

    # --- Points Logic ---
    focus_minutes = focus_seconds // 60
    break_minutes = break_seconds // 60

    work_points = focus_minutes
    break_points = break_minutes
    task_points = done_todos * 10
    hydration_points = int(consumed_ml // 100)
    # Setiap gerakan unik stretching = 15 poin exercise (maksimal 6 gerakan per hari = 90 poin)
    exercise_points = stretching_count * 15

    total_points = work_points + break_points + task_points + hydration_points + exercise_points

    # --- WLB Balance Percentages ---
    total_wlb_activity = work_points + break_points + exercise_points
    if total_wlb_activity > 0:
        work_pct = round((work_points / total_wlb_activity) * 100, 1)
        rest_pct = round((break_points / total_wlb_activity) * 100, 1)
        exercise_pct = round((exercise_points / total_wlb_activity) * 100, 1)
    else:
        work_pct, rest_pct, exercise_pct = 0.0, 0.0, 0.0

    efficiency = round(min(work_pct, 100.0), 1)

    return {
        "date": today.isoformat(),
        "focus_time_seconds": focus_seconds,
        "break_time_seconds": break_seconds,
        "points": total_points,
        "tasks": {
            "total": total_todos,
            "done": done_todos,
            "completion_rate": completion_rate,
        },
        "balance": {
            "work_percent": work_pct,
            "rest_percent": rest_pct,
            "exercise_percent": exercise_pct,
            "efficiency_score": efficiency,
        },
        "hydration": {
            "consumed_ml": consumed_ml,
            "target_ml": target_ml,
            "progress_percent": hydration_pct,
        },
        "stretching": {
            "sessions_today": stretching_count,
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


async def get_leaderboard(db: AsyncSession, target_date=None) -> list[dict]:
    from app.models.user import User
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    # 1. Get total pomodoro seconds per user TODAY
    pomodoro_res = await db.execute(
        select(
            PomodoroSession.user_id,
            func.coalesce(func.sum(PomodoroSession.actual_duration_seconds), 0)
        ).where(
            and_(
                PomodoroSession.status == "completed",
                PomodoroSession.session_date == target_date
            )
        ).group_by(PomodoroSession.user_id)
    )
    pomodoro_map = {row[0]: row[1] for row in pomodoro_res.all()}

    # 2. Get done todos per user TODAY
    todo_res = await db.execute(
        select(
            Todo.user_id,
            func.count(Todo.id)
        ).where(
            and_(
                Todo.status == "done",
                Todo.task_date == target_date
            )
        ).group_by(Todo.user_id)
    )
    todo_map = {row[0]: row[1] for row in todo_res.all()}

    # 3. Get hydration ml per user TODAY
    hydration_res = await db.execute(
        select(
            HydrationLog.user_id,
            func.coalesce(func.sum(HydrationLog.amount_ml), 0.0)
        ).where(
            HydrationLog.log_date == target_date
        ).group_by(HydrationLog.user_id)
    )
    hydration_map = {row[0]: row[1] for row in hydration_res.all()}

    # 4. Get unique stretching exercises per user TODAY
    target_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    target_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    stretching_res = await db.execute(
        select(
            StretchingSession.user_id,
            func.count(func.distinct(StretchingSession.exercise_id))
        ).where(
            and_(
                StretchingSession.status == "completed",
                StretchingSession.started_at >= target_start,
                StretchingSession.started_at <= target_end
            )
        ).group_by(StretchingSession.user_id)
    )
    stretching_map = {row[0]: min(row[1], 6) for row in stretching_res.all()}

    # 5. Get all active users
    users_res = await db.execute(
        select(User.id, User.full_name, User.email, User.avatar_url).where(User.is_active == True)
    )
    users = users_res.all()

    leaderboard = []
    for u in users:
        uid = u.id
        pomo_secs = pomodoro_map.get(uid, 0)
        todos_count = todo_map.get(uid, 0)
        hydro_ml = hydration_map.get(uid, 0.0)
        stretch_count = stretching_map.get(uid, 0)

        # Point calculation identical to dashboard logic
        points = (pomo_secs // 60) + (todos_count * 10) + int(hydro_ml // 100) + (stretch_count * 15)

        leaderboard.append({
            "user_id": str(uid),
            "name": u.full_name or u.email,
            "avatar_url": u.avatar_url,
            "points": points
        })

    # Sort descending by points
    leaderboard.sort(key=lambda x: x["points"], reverse=True)

    # Assign ranks
    for idx, item in enumerate(leaderboard):
        item["rank"] = idx + 1

    return leaderboard
