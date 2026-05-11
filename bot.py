import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from utils.db import init as db_init
from middlewares.middlewares import UserCheckMiddleware
from handlers import start, menu, topics, speaking, history, admin
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

