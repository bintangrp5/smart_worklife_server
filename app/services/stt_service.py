"""
Speech-to-Text Service.
Menggunakan OpenAI Whisper API sebagai provider utama.
Ganti implementasi di fungsi `transcribe_audio` jika ingin menggunakan provider lain.
"""
import io
import wave
from typing import Optional
from openai import AsyncOpenAI

from app.core.config import settings


async def transcribe_audio(
    audio_bytes: bytes,
    filename: Optional[str] = "audio.wav",
) -> tuple[str, Optional[int]]:
    """
    Konversi audio bytes ke teks menggunakan Whisper API.

    Returns:
        transcript (str): Teks hasil transkripsi.
        duration_seconds (int | None): Estimasi durasi audio.
    """
    if not settings.OPENAI_API_KEY:
        # Fallback mock jika API key belum diisi
        return "[TRANSCRIPT PLACEHOLDER — Isi OPENAI_API_KEY di .env untuk mengaktifkan Speech-to-Text]", None

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename or "audio.wav"

    response = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="id",
        response_format="verbose_json",
    )

    transcript = response.text
    duration_seconds = int(response.duration) if hasattr(response, "duration") and response.duration else None

    return transcript, duration_seconds
