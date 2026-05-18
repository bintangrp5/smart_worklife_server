"""Router — Smart To-Do List."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user_id
from app.crud import todo as crud
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/todos", tags=["Smart To-Do List"])


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    data: TodoCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await crud.create_todo(db, user_id, data)


@router.get("/", response_model=list[TodoResponse])
async def list_todos(
    category: Optional[str] = Query("all", pattern="^(all|important|today|tomorrow)$"),
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(pending|done)$"),
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await crud.get_todos(db, user_id, category=category, status=status_filter)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    todo = await crud.get_todo_by_id(db, todo_id, user_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan.")
    return todo


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: uuid.UUID,
    data: TodoUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    todo = await crud.get_todo_by_id(db, todo_id, user_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan.")
    return await crud.update_todo(db, todo, data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    todo = await crud.get_todo_by_id(db, todo_id, user_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan.")
    await crud.delete_todo(db, todo)
