"""CRUD operations for Smart To-Do List."""
import uuid
from datetime import datetime, timezone, date, timedelta
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


async def create_todo(db: AsyncSession, user_id: uuid.UUID, data: TodoCreate) -> Todo:
    todo = Todo(user_id=user_id, **data.model_dump())
    db.add(todo)
    await db.flush()
    await db.refresh(todo)
    return todo


async def get_todos(
    db: AsyncSession,
    user_id: uuid.UUID,
    category: Optional[str] = "all",
    status: Optional[str] = None,
) -> list[Todo]:
    today = datetime.now(timezone.utc).date()
    tomorrow = today + timedelta(days=1)

    filters = [Todo.user_id == user_id]

    if status:
        filters.append(Todo.status == status)

    if category == "important":
        filters.append(Todo.priority == "important")
    elif category == "today":
        filters.append(Todo.task_date == today)
    elif category == "tomorrow":
        filters.append(Todo.task_date == tomorrow)

    result = await db.execute(
        select(Todo).where(and_(*filters)).order_by(Todo.created_at.desc())
    )
    return result.scalars().all()


async def get_todo_by_id(db: AsyncSession, todo_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Todo]:
    result = await db.execute(
        select(Todo).where(and_(Todo.id == todo_id, Todo.user_id == user_id))
    )
    return result.scalar_one_or_none()


async def update_todo(db: AsyncSession, todo: Todo, data: TodoUpdate) -> Todo:
    update_data = data.model_dump(exclude_unset=True)

    # Jika status berubah menjadi 'done', catat waktu penyelesaian
    if update_data.get("status") == "done" and todo.status != "done":
        update_data["completed_at"] = datetime.now(timezone.utc)
    elif update_data.get("status") == "pending":
        update_data["completed_at"] = None

    for field, value in update_data.items():
        setattr(todo, field, value)

    await db.flush()
    await db.refresh(todo)
    return todo


async def delete_todo(db: AsyncSession, todo: Todo) -> None:
    await db.delete(todo)
    await db.flush()
