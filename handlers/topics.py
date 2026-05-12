from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import db, ai
import random
import os
from keyboards import keyboards as kb

router = Router()

class TopicPractice(StatesGroup):
    waiting_voice = State()

@router.callback_query(F.data.startswith("start_topic_"))
async def start_specific_topic(cb: CallbackQuery, state: FSMContext, user):
    topic_id = int(cb.data.split("_")[-1])
    # Bazadan topikni olish
    conn = db.sqlite3.connect(db.DB_PATH)
    topic = conn.execute("SELECT * FROM topics WHERE id=?", (topic_id,)).fetchone()
    conn.close()

    if not topic:
        await cb.answer("❌ Topik topilmadi.", show_alert=True)
        return

    text = f"""
━━━━━━━━━━━━━━━━━━━━━━
🎤 {topic[3]} Speaking — Part {topic[1]}
📊 Daraja: {topic[2]}
━━━━━━━━━━━━━━━━━━━━━━

📌 {topic[4]}

━━━━━━━━━━━━━━━━━━━━━━
🎙 <b>Hozirroq audio yuboring va AI feedback oling!</b>
"""
    await state.set_state(TopicPractice.waiting_voice)
    await state.update_data(current_topic_id=topic_id, current_topic_text=topic[4])
    
    await cb.message.answer(text, parse_mode="HTML")
    await cb.answer()

@router.message(TopicPractice.waiting_voice, F.voice)
async def handle_topic_voice(message: Message, state: FSMContext, user):
    data = await state.get_data()
    loading = await message.answer("⏳ <b>Auda tahlil qilinmoqda...</b>", parse_mode="HTML")
    
    # Audio yuklab olish va transkripsiya
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"voices/practice_{file_id}.ogg"
    os.makedirs("voices", exist_ok=True)
    await message.bot.download_file(file.file_path, file_path)
    
    transcript = await ai.transcribe(file_path)
    os.remove(file_path)
    
    # AI orqali feedback olish
    feedback = await ai.get_feedback(transcript, data['current_topic_text'], user['lang'], part=1)
    
    # Bazaga saqlash
    db.save_result(user['tg_id'], data['current_topic_id'], transcript, feedback['band'], feedback['cefr'], feedback['full_text'], feedback['grammar'], feedback['vocab'])
    
    await loading.delete()
    await message.answer(feedback['full_text'], parse_mode="HTML", reply_markup=kb.main_menu(user['lang']))
    await state.clear()

# Eski handlerlar (o'zgarishsiz qoladi yoki kerak bo'lsa yangilanadi)
@router.callback_query(F.data == "topics")
async def select_exam(cb: CallbackQuery, user):
    lang = user['lang']
    text = "🎯 Qaysi turdagi topik kerak?" if lang == 'uz' else "🎯 Which type of topic?"
    await cb.message.edit_text(text, reply_markup=kb.exam_kb(lang))

@router.callback_query(F.data.startswith("exam_"))
async def select_part(cb: CallbackQuery, user):
    exam = cb.data.split("_")[1]
    text = "🎤 Partni tanlang:" if user['lang'] == 'uz' else "🎤 Choose Part:"
    b = kb.InlineKeyboardBuilder()
    for i in [1, 2, 3]:
        b.button(text=f"Part {i}", callback_data=f"part_{i}_{exam}")
    b.button(text="Tasodifiy" if user['lang'] == 'uz' else "Random", callback_data=f"part_0_{exam}")
    b.button(text="🏠 Menu", callback_data="menu")
    b.adjust(2)
    await cb.message.edit_text(text, reply_markup=b.as_markup())

@router.callback_query(F.data.startswith("part_"))
async def show_topic(cb: CallbackQuery, user, state: FSMContext):
    parts = cb.data.split("_")
    part_id = int(parts[1])
    exam = parts[2]
    
    topics = db.get_filtered_topics(exam, part_id if part_id != 0 else None, user['level'])
    
    if not topics:
        text = "❌ Hozircha bu turda topiklar yo'q." if user['lang'] == 'uz' else "❌ No topics available."
        await cb.message.edit_text(text, reply_markup=kb.kb(("🏠 Menu", "menu")))
        return

    topic = random.choice(topics)
    
    text = f"""
━━━━━━━━━━━━━━━━━━━━━━
🎤 {topic[3]} Speaking — Part {topic[1]}
📊 Daraja: {topic[2]}
━━━━━━━━━━━━━━━━━━━━━━

📌 {topic[4]}

⏱️ Gapirish vaqti: {'1–2 daqiqa' if topic[1] == 2 else '30-60 soniya'}
━━━━━━━━━━━━━━━━━━━━━━
🎙 <b>Audio yuboring!</b>
"""
    await state.set_state(TopicPractice.waiting_voice)
    await state.update_data(current_topic_id=topic[0], current_topic_text=topic[4])
    
    await cb.message.answer(text, parse_mode="HTML")
    await cb.answer()
