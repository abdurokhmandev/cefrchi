import asyncio
<<<<<<< HEAD
import os
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from utils.db import init as db_init
from middlewares.middlewares import UserCheckMiddleware
from handlers import start, menu, topics, speaking, history, admin, vocab
from web_server import create_app
from aiohttp import web


async def main():
    logging.basicConfig(level=logging.INFO)
    db_init()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Middleware
    dp.message.outer_middleware(UserCheckMiddleware())
    dp.callback_query.outer_middleware(UserCheckMiddleware())
    
    # Routerlarni ulash
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(topics.router)
    dp.include_router(speaking.router)
    dp.include_router(vocab.router)
    dp.include_router(history.router)
    
    # Web serverni sozlash
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Railway yoki boshqa hostinglar uchun PORT ni olish
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"✅ Bot and Web Server started on port {port}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping...")

=======
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config import config
from database.engine import engine
from database.models import Base
from services.scheduler import setup_scheduler

# Handlers import
from handlers.start import router as start_router
from handlers.speaking import router as speaking_router
from handlers.writing import router as writing_router
from handlers.progress import router as progress_router
from handlers.vocabulary import router as vocab_router
from handlers.mock import router as mock_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def init_db():
    async with engine.begin() as conn:
        # Barcha jadvallarni yaratish
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await init_db()
    
    bot = Bot(token=config.bot_token.get_secret_value())
    storage = RedisStorage.from_url(config.redis_url)
    dp = Dispatcher(storage=storage)
    
    # Routerlarni qo'shish
    dp.include_router(start_router)
    dp.include_router(speaking_router)
    dp.include_router(writing_router)
    dp.include_router(progress_router)
    dp.include_router(vocab_router)
    dp.include_router(mock_router)
    
    # Scheduler ishga tushirish
    setup_scheduler(bot)
    
    logger.info("Bot ishga tushirildi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
>>>>>>> 1d2f1c3 (Initial commit)
