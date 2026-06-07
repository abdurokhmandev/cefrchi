=======
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

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
    storage = MemoryStorage()
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

