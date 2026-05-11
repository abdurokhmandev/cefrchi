from aiogram import Router, F
from aiogram.types import CallbackQuery
import db
import keyboards as kb

router = Router()

@router.callback_query(F.data == "menu")
async def show_menu(cb: CallbackQuery, user):
    streak = user.get('streak', 0)
    streak_text = f"\n🔥 <b>Streak: {streak} kun</b>" if user['lang'] == 'uz' else f"\n🔥 <b>Streak: {streak} days</b>"
    
    text = f"🏠 <b>Bosh menyu</b>\n" if user['lang'] == 'uz' else f"🏠 <b>Main Menu</b>\n"
    text += f"👤 {user['full_name']}\n"
    text += f"📊 Level: {user['level']} | {user['exam']}"
    text += streak_text
    
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb.main_menu(user['lang']))


@router.callback_query(F.data == "settings")
async def show_settings(cb: CallbackQuery, user):
    await cb.message.edit_text(f"⚙️ Sozlamalar / Settings", reply_markup=kb.settings_menu(user['lang']))

@router.callback_query(F.data == "set_lang")
async def set_lang(cb: CallbackQuery):
    await cb.message.edit_text("🌐 Tilni tanlang / Choose language:", reply_markup=kb.lang_kb())

@router.callback_query(F.data.startswith("lang_"))
async def update_lang(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    db.update_user_field(cb.from_user.id, "lang", lang)
    await cb.answer("✅ Updated!")
    user = db.get_user(cb.from_user.id)
    await cb.message.edit_text(f"🏠 Bosh menyu / Main Menu", reply_markup=kb.main_menu(user['lang']))

@router.callback_query(F.data == "set_level")
async def set_level(cb: CallbackQuery):
    await cb.message.edit_text("📈 Darajani tanlang / Choose level:", reply_markup=kb.level_kb())

@router.callback_query(F.data.startswith("level_"))
async def update_level(cb: CallbackQuery):
    level = cb.data.split("_")[1]
    db.update_user_field(cb.from_user.id, "level", level)
    await cb.answer("✅ Updated!")
    user = db.get_user(cb.from_user.id)
    await cb.message.edit_text(f"⚙️ Sozlamalar / Settings", reply_markup=kb.settings_menu(user['lang']))
