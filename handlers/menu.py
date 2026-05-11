from aiogram import Router, F
from aiogram.types import CallbackQuery
import db
import keyboards as kb
from i18n import t

router = Router()

@router.callback_query(F.data == "menu")
async def show_menu(cb: CallbackQuery, user):
    lang = user['lang']
    welcome = t('main_menu_msg', lang, name=user['full_name'])
    await cb.message.edit_text(welcome, reply_markup=kb.main_menu(lang))

@router.callback_query(F.data == "topics")
async def show_topics(cb: CallbackQuery, user):
    lang = user['lang']
    await cb.message.edit_text("📚 Topiclar bo'limi tez kunda ishga tushadi.", reply_markup=kb.back_kb(lang))

@router.callback_query(F.data == "vocab")
async def show_vocab(cb: CallbackQuery, user):
    lang = user['lang']
    await cb.message.edit_text("📖 Maxsus Vocabularylar bo'limi tez kunda ishga tushadi.", reply_markup=kb.back_kb(lang))

@router.callback_query(F.data == "settings")
async def show_settings(cb: CallbackQuery, user):
    lang = user['lang']
    text = f"⚙️ <b>Sozlamalar</b>\n\n👤 Ism: {user['full_name']}\n📈 Daraja: {user['level']}\n🎯 Imtihon: {user['exam']}\n🌐 Til: {user['lang'].upper()}"
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb.back_kb(lang))

@router.callback_query(F.data == "contact")
async def show_contact(cb: CallbackQuery, user):
    lang = user['lang']
    await cb.message.edit_text("📩 Savol va takliflar uchun: @abdurokhmandev", reply_markup=kb.back_kb(lang))

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
