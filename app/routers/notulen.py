"""Router — Smart Notulen."""
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user_id
from app.crud import notulen as crud
from app.schemas.notulen import NotulenSave, NotulenResponse, NotulenListItem
from app.services.stt_service import transcribe_audio
from app.services.ai_service import generate_summary

router = APIRouter(prefix="/notulens", tags=["Smart Notulen"])


@router.post("/upload", response_model=NotulenResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    file: UploadFile = File(..., description="File audio rapat (WAV / MP3 / M4A, maks 60 menit)"),
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Upload file audio → Speech-to-Text → simpan transcript sebagai draft notulen.
    """
    allowed_types = {"audio/wav", "audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/ogg"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Format file tidak didukung: {file.content_type}")

    audio_bytes = await file.read()
    transcript, duration_seconds = await transcribe_audio(audio_bytes, filename=file.filename)

    notulen = await crud.create_notulen(
        db,
        user_id=user_id,
        transcript=transcript,
        duration_seconds=duration_seconds,
        audio_url=None,  # Bisa diisi jika menyimpan ke cloud storage
    )
    return notulen


@router.post("/{notulen_id}/generate-summary", response_model=NotulenResponse)
async def generate_ai_summary(
    notulen_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Kirim transcript ke LLM → generate ringkasan + action items.
    """
    notulen = await crud.get_notulen(db, notulen_id, user_id)
    if not notulen:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan.")
    if not notulen.transcript:
        raise HTTPException(status_code=400, detail="Transcript kosong. Upload audio terlebih dahulu.")

    summary, action_items = await generate_summary(notulen.transcript)
    return await crud.update_summary(db, notulen, summary, action_items)


@router.post("/{notulen_id}/save", response_model=NotulenResponse)
async def save_notulen(
    notulen_id: uuid.UUID,
    data: NotulenSave,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Simpan notulen ke arsip dengan judul dan tanggal rapat."""
    notulen = await crud.get_notulen(db, notulen_id, user_id)
    if not notulen:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan.")
    return await crud.save_notulen(db, notulen, data)


@router.get("/", response_model=list[NotulenListItem])
async def list_notulens(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    notulens = await crud.list_notulens(db, user_id)
    return [
        NotulenListItem(
            id=n.id,
            title=n.title,
            meeting_date=n.meeting_date,
            duration_seconds=n.duration_seconds,
            has_summary=bool(n.summary),
            created_at=n.created_at,
        )
        for n in notulens
    ]


@router.get("/{notulen_id}", response_model=NotulenResponse)
async def get_notulen(
    notulen_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    notulen = await crud.get_notulen(db, notulen_id, user_id)
    if not notulen:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan.")
    return notulen


@router.delete("/{notulen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notulen(
    notulen_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    notulen = await crud.get_notulen(db, notulen_id, user_id)
    if not notulen:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan.")
    await crud.delete_notulen(db, notulen)
