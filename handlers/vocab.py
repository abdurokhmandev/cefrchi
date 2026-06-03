from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from utils import db
from keyboards import keyboards as kb

router = Router()

@router.callback_query(F.data == "vocab")
async def show_vocab_categories(cb: CallbackQuery, user):
    lang = user['lang']
    # Foydalanuvchi exam va leveliga mos lug'atlarni olish
    vocabs = db.get_all_vocab(user['exam'], user['level'])
    
    if not vocabs:
        text = "❌ Hozircha sizning darajangizga mos lug'atlar yo'q." if lang == 'uz' else "❌ No vocabularies available for your level."
        await cb.message.edit_text(text, reply_markup=kb.back_kb(lang))
        return

    text = "📖 <b>Maxsus Lug'atlar</b>\n\nMavzuni tanlang:" if lang == 'uz' else "📖 <b>Special Vocabularies</b>\n\nChoose a topic:"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    b = InlineKeyboardBuilder()
    for v in vocabs:
        b.button(text=f"🔸 {v[1]}", callback_data=f"v_show_{v[0]}")
    
    b.button(text="🏠 Menu", callback_data="menu")
    b.adjust(1)
    
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=b.as_markup())

@router.callback_query(F.data.startswith("v_show_"))
async def show_specific_vocab(cb: CallbackQuery, user):
    v_id = int(cb.data.split("_")[-1])
    lang = user['lang']
    
    conn = db.sqlite3.connect(db.DB_PATH)
    v = conn.execute("SELECT * FROM vocabularies WHERE id=?", (v_id,)).fetchone()
    conn.close()
    
    if not v:
        await cb.answer("❌ Lug'at topilmadi.", show_alert=True)
        return
        
    text = f"📖 <b>Mavzu: {v[1]}</b>\n\n{v[2]}"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ Orqaga" if lang == 'uz' else "⬅️ Back", callback_data="vocab")
    b.button(text="🏠 Menu", callback_data="menu")
    b.adjust(2)
    
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=b.as_markup())
