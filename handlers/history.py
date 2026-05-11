from aiogram import Router, F
from aiogram.types import CallbackQuery
import db
import keyboards as kb

router = Router()

@router.callback_query(F.data.startswith("history_"))
async def show_history(cb: CallbackQuery, user):
    offset = int(cb.data.split("_")[1])
    results = db.get_user_results(user['tg_id'], limit=5, offset=offset)
    
    if not results and offset == 0:
        text = "📊 <b>Sizda hali natijalar yo'q.</b>\n\nGapirishni boshlash uchun '🎤 Speaking boshlash' tugmasini bosing."
        await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb.kb(("🏠 Menu", "menu")))
        return

    text = f"📊 <b>MENING NATIJALARIM</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
    
    for r in results:
        topic_id, band, cefr, date, topic_text = r
        text += f"📌 {topic_text[:30]}...\n🎯 Band {band} | 📊 {cefr} | 📅 {date[:10]}\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━"
    
    # Pagination tugmalari
    builder = kb.InlineKeyboardBuilder()
    if offset >= 5:
        builder.button(text="◀️", callback_data=f"history_{offset-5}")
    builder.button(text="🏠 Menu", callback_data="menu")
    if len(results) == 5:
        builder.button(text="▶️", callback_data=f"history_{offset+5}")
    builder.adjust(3)
    
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())
