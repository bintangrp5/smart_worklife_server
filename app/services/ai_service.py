"""
AI Summary Service.
Menggunakan Google Gemini API (google-genai SDK) untuk menghasilkan ringkasan
dan action items dari transcript rapat.
"""
import json

from google import genai
from google.genai import types

from app.core.config import settings

SUMMARY_PROMPT = """
Kamu adalah asisten notulis profesional. Berikut adalah transkrip rapat:

---
{transcript}
---

Tugasmu:
1. Buat RINGKASAN singkat dan padat dari rapat di atas (maksimal 5 paragraf).
2. Ekstrak daftar ACTION ITEMS yang perlu ditindaklanjuti.

Balas HANYA dalam format JSON berikut (tanpa markdown/code block):
{{
  "summary": "Ringkasan rapat di sini...",
  "action_items": [
    "Action item 1",
    "Action item 2"
  ]
}}
"""


async def generate_summary(transcript: str) -> tuple[str, list[str]]:
    """
    Generate ringkasan dan action items dari transcript menggunakan Gemini.

    Returns:
        summary (str): Ringkasan rapat.
        action_items (list[str]): Daftar poin tindakan.
    """
    if not settings.GEMINI_API_KEY:
        return (
            "[SUMMARY PLACEHOLDER - Isi GEMINI_API_KEY di .env untuk mengaktifkan AI Summary]",
            ["[Isi GEMINI_API_KEY di .env]"],
        )

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = SUMMARY_PROMPT.format(transcript=transcript)

    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    raw = response.text.strip()
    # Bersihkan jika ada markdown code block
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    data = json.loads(raw)
    summary = data.get("summary", "")
    action_items = data.get("action_items", [])

    return summary, action_items
