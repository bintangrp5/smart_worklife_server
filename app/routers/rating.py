import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user_id
from app.crud import rating as crud
from app.schemas.rating import AppRatingCreate, AppRatingResponse

router = APIRouter(prefix="/ratings", tags=["App Ratings"])

@router.post("", response_model=AppRatingResponse)
async def submit_rating(
    data: AppRatingCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Kirim atau perbarui rating untuk sebuah fitur."""
    return await crud.create_or_update_rating(db, user_id, data)

@router.get("/me", response_model=list[AppRatingResponse])
async def get_my_ratings(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Ambil semua rating yang pernah dikirimkan oleh user ini."""
    return await crud.get_user_ratings(db, user_id)
