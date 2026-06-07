import logging
from openai import AsyncOpenAI
from config import config

logger = logging.getLogger(__name__)

# OpenAI uchun alohida client (Whisper)
client = AsyncOpenAI(
    api_key=config.openai_api_key.get_secret_value()
)

async def transcribe_audio(file_path: str) -> str:
    """Telegramdan olingan audio faylni Whisper yordamida matnga o'giradi."""
    try:
        logger.info("Ovozni matnga o'girish boshlandi (Whisper)...")
        with open(file_path, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                timeout=30.0
            )
            return transcript.text
    except Exception as e:
        logger.error(f"Whisper API xatoligi yuz berdi: {e}")
        raise
