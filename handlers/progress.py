import logging
from aiogram import Router, F, types
from aiogram.filters import Command

from database.engine import get_session
from database.crud import get_user, get_recent_scores

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "menu_progress")
async def show_progress_cb(callback: types.CallbackQuery):
    await _send_progress(callback.message, callback.from_user.id)
    await callback.answer()

@router.message(Command("progress", "stats"))
async def show_progress_cmd(message: types.Message):
    await _send_progress(message, message.from_user.id)

async def _send_progress(message: types.Message, user_id: int):
    async for session in get_session():
        user = await get_user(session, user_id)
        if not user:
            await message.answer("Foydalanuvchi ma'lumotlari topilmadi.")
            return

        scores = await get_recent_scores(session, user_id, 20)
        
        speaking_scores = [s.band_score for s in scores if s.skill == 'speaking']
        writing_scores = [s.band_score for s in scores if s.skill == 'writing']
        
        spk_avg = sum(speaking_scores) / len(speaking_scores) if speaking_scores else 0.0
        wrt_avg = sum(writing_scores) / len(writing_scores) if writing_scores else 0.0
        
        days_left = "Noma'lum"
        if user.exam_date:
            from datetime import date
            delta = user.exam_date - date.today()
            if delta.days >= 0:
                days_left = f"{delta.days} kun"
            else:
                days_left = "Imtihon o'tib ketgan"

        progress_text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Sizning progressing\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 {user.full_name}\n"
            f"🎓 CEFR: {user.cefr_level}  →  🎯 Maqsad: {user.target_band}\n"
            f"📅 Imtihon: {days_left}\n\n"
            f"📈 O'rtacha natijalar:\n"
            f"🎙 Speaking:   {spk_avg:.1f} ⭐️\n"
            f"✍️ Writing:    {wrt_avg:.1f} ⭐️\n\n"
            f"🔥 Streak: {user.streak_days} kun\n"
            f"⭐ XP: {user.xp_total} ball\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        from keyboards.menus import get_back_menu
        # Callback query yoki oddiy message ekanligini tekshiramiz
        if message.text is not None and message.text.startswith("/"):
            await message.answer(progress_text, reply_markup=get_back_menu())
        else:
            await message.edit_text(progress_text, reply_markup=get_back_menu())
