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
    Jika Gemini gagal atau API Key tidak valid, otomatis fallback ke Groq.

    Returns:
        summary (str): Ringkasan rapat.
        action_items (list[str]): Daftar poin tindakan.
    """
    use_groq = False
    
    # Deteksi jika API Key Gemini bawaan tidak valid (biasanya API key mulai dengan AIzaSy)
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("AQ."):
        use_groq = True

    if not use_groq:
        try:
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
        except Exception as e:
            print(f"⚠️ Gemini API error, falling back to Groq: {e}")
            use_groq = True

    # FALLBACK KE GROQ
    if use_groq:
        if not settings.GROQ_API_KEY:
            return (
                "[SUMMARY PLACEHOLDER - Isi GROQ_API_KEY atau GEMINI_API_KEY di .env untuk AI Summary]",
                ["[Isi API Key di .env]"],
            )
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            prompt = SUMMARY_PROMPT.format(transcript=transcript)
            
            # Gunakan llama-3.3-70b-versatile untuk kualitas terbaik dan kecepatan tinggi
            model_to_use = "llama-3.3-70b-versatile"
            
            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model_to_use,
                response_format={"type": "json_object"},
            )
            
            raw = chat_completion.choices[0].message.content.strip()
            data = json.loads(raw)
            summary = data.get("summary", "")
            action_items = data.get("action_items", [])
            return summary, action_items
        except Exception as e:
            print(f"❌ Groq Summary error: {e}")
            return (
                f"[Gagal menghasilkan ringkasan otomatis karena error: {e}]",
                [],
            )


REFINE_PROMPT = """
Kamu adalah asisten editor transkrip profesional. Tugasmu adalah memperbaiki, merapikan, dan memperbagus hasil transkripsi suara (Speech-to-Text) berikut agar menjadi bahasa Indonesia yang baik, benar, terstruktur, mudah dibaca, dan profesional.

Aturan:
1. Perbaiki ejaan kata yang salah (typo), tambahkan tanda baca yang tepat (titik, koma, huruf kapital), dan pisahkan menjadi paragraf yang logis jika terlalu panjang.
2. Hapus kata-kata pengisi (filler words seperti "eee", "aaa", "hmm", "anu", "itu") dan kata-kata yang terulang tidak sengaja.
3. JANGAN menambah informasi baru yang tidak ada pada transkrip asli atau mengubah makna inti pembicaraan.
4. Pertahankan gaya bahasa asli (formal atau semi-formal).

Transkrip asli:
---
{transcript}
---

Tuliskan transkrip hasil perbaikan di bawah ini (hanya teks transkrip hasil perbaikan saja, jangan tambahkan intro, outro, penjelasan, atau tanda kutip pembungkus):
"""


async def refine_transcript(transcript: str) -> str:
    """
    Memperbaiki dan memperbagus teks transkripsi menggunakan LLM (Gemini/Groq).
    """
    if not transcript or not transcript.strip():
        return ""

    use_groq = False
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("AQ."):
        use_groq = True

    if not use_groq:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = REFINE_PROMPT.format(transcript=transcript)

            response = await client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Gemini Refine error, falling back to Groq: {e}")
            use_groq = True

    if use_groq:
        if not settings.GROQ_API_KEY:
            return transcript  # No key, return original

        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            prompt = REFINE_PROMPT.format(transcript=transcript)

            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Groq Refine error: {e}")
            return transcript



