"""
Speech-to-Text Service.
Menggunakan Groq Whisper API untuk transkripsi audio.
Groq gratis, cepat, dan akurat untuk bahasa Indonesia.
"""
import io
from typing import Optional
from groq import AsyncGroq

from app.core.config import settings


async def transcribe_audio(
    audio_bytes: bytes,
    filename: Optional[str] = "audio.m4a",
) -> tuple[str, Optional[int]]:
    """
    Konversi audio bytes ke teks menggunakan Groq Whisper API.

    Returns:
        transcript (str): Teks hasil transkripsi.
        duration_seconds (int | None): Estimasi durasi audio.
    """
    if not settings.GROQ_API_KEY:
        return "[TRANSCRIPT PLACEHOLDER — Isi GROQ_API_KEY di .env untuk mengaktifkan Speech-to-Text]", None

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    # Tentukan ekstensi file
    ext = "m4a"
    if filename:
        fname_lower = filename.lower()
        if fname_lower.endswith(".wav"):
            ext = "wav"
        elif fname_lower.endswith(".mp3"):
            ext = "mp3"
        elif fname_lower.endswith(".ogg"):
            ext = "ogg"
        elif fname_lower.endswith(".webm"):
            ext = "webm"

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = f"audio.{ext}"

    transcription = await client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-large-v3-turbo",
        language="id",
        response_format="verbose_json",
    )

    transcript = transcription.text.strip()
    duration_seconds = int(transcription.duration) if hasattr(transcription, "duration") and transcription.duration else None

    return transcript, duration_seconds
