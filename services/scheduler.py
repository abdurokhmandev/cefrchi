import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

from database.engine import get_session
from database.crud import get_all_users

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

async def send_daily_reminders(bot):
    """Har kuni ertalab soat 09:00 da foydalanuvchilarga eslatma yuborish"""
    logger.info("Kunlik eslatmalar yuborilmoqda...")
    
    async for session in get_session():
        users = await get_all_users(session)
        for user in users:
            if not user.is_active:
                continue
                
            try:
                # Eslatma matni
                text = (
                    f"☀️ Xayrli tong, {user.full_name}!\n"
                    f"Bugungi vazifa: Speaking mashq qilishni unutmang\n"
                    f"🔥 Streak: {user.streak_days} kun\n"
                    f"Davom etish uchun menyuga o'ting: /start"
                )
                await bot.send_message(user.user_id, text)
            except Exception as e:
                logger.warning(f"Foydalanuvchiga xabar yuborishda xatolik ({user.user_id}): {e}")

async def check_streaks(bot):
    """Har kuni kechasi streaklarni tekshirish"""
    logger.info("Streaklar tekshirilmoqda...")
    async for session in get_session():
        users = await get_all_users(session)
        for user in users:
            # Agar last_activity kechagi kundan oldin bo'lsa
            if user.last_activity.date() < (datetime.utcnow().date() - timedelta(days=1)):
                try:
                    await bot.send_message(user.user_id, "⚠️ Streakingiz uzilmoqda! Bugun kamida 1 ta mashq bajaring!")
                    user.streak_days = 0
                    await session.commit()
                except:
                    pass

def setup_scheduler(bot):
    # Har kuni 09:00 da
    scheduler.add_job(send_daily_reminders, 'cron', hour=9, minute=0, args=[bot])
    # Har kuni 23:00 da (Streak eslatmasi)
    scheduler.add_job(check_streaks, 'cron', hour=23, minute=0, args=[bot])
    scheduler.start()
