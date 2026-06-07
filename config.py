<<<<<<< HEAD
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Adminlarni xavfsiz o'qish
admin_str = os.getenv("ADMIN_IDS", "").strip()
if admin_str:
    ADMIN_IDS = list(map(int, admin_str.split(",")))
else:
    ADMIN_IDS = []

# Railway-da WEBAPP_URL o'zgaruvchisiga berilgan domenni yozing
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://abdurokhman.uz/cefrchi.html")

# Ma'lumotlar bazasi manzili (Railway Volume uchun)
DB_PATH = os.getenv("DB_PATH", "data/bot.db")

# Veb Admin login ma'lumotlari
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "cefr123")
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_32_chars_long!!") # 32 chars for Fernet



=======
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import List

class Settings(BaseSettings):
    """
    Bot va boshqa xizmatlar uchun sozlamalar (Environment variables).
    """
    bot_token: SecretStr
    openrouter_api_key: SecretStr
    openai_api_key: SecretStr
    database_url: str
    # redis_url removed, using in‑memory storage
    admin_ids: List[int]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

config = Settings()
>>>>>>> 1d2f1c3 (Initial commit)
