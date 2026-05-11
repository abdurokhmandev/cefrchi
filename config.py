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
DB_PATH = os.getenv("DB_PATH", "bot.db")



