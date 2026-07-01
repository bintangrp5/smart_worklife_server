import asyncio
from app.services.stt_service import transcribe_audio

async def test():
    try:
        # Create a small dummy valid wav or m4a byte array
        audio_bytes = b"dummy"
        transcript, duration = await transcribe_audio(audio_bytes, "test.m4a")
        print("Success:", transcript)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
