from aiogram import Router, F
from aiogram.types import CallbackQuery
import db
import random
import keyboards as kb

router = Router()

@router.callback_query(F.data == "topic")
async def select_exam(cb: CallbackQuery, user):
    text = "🎯 Qaysi turdagi topik kerak?" if user['lang'] == 'uz' else "🎯 Which type of topic?"
    await cb.message.edit_text(text, reply_markup=kb.exam_kb())

@router.callback_query(F.data.startswith("exam_"))
async def select_part(cb: CallbackQuery, user):
    exam = cb.data.split("_")[1]
    # Vaqtincha sessionda saqlash (biz buni callback_data ga tiqamiz)
    text = "🎤 Partni tanlang:" if user['lang'] == 'uz' else "🎤 Choose Part:"
    
    # Callback_data ni part_X_EXAM ko'rinishida qilamiz
    b = kb.InlineKeyboardBuilder()
    for i in [1, 2, 3]:
        b.button(text=f"Part {i}", callback_data=f"part_{i}_{exam}")
    b.button(text="Tasodifiy" if user['lang'] == 'uz' else "Random", callback_data=f"part_0_{exam}")
    b.button(text="🏠 Menu", callback_data="menu")
    b.adjust(2)
    await cb.message.edit_text(text, reply_markup=b.as_markup())

@router.callback_query(F.data.startswith("part_"))
async def show_topic(cb: CallbackQuery, user):
    parts = cb.data.split("_")
    part_id = int(parts[1])
    exam = parts[2]
    
    topics = db.get_filtered_topics(exam, part_id if part_id != 0 else None, user['level'])
    
    if not topics:
        text = "❌ Hozircha bu turda topiklar yo'q." if user['lang'] == 'uz' else "❌ No topics available."
        await cb.message.edit_text(text, reply_markup=kb.kb(("🏠 Menu", "menu")))
        return

    topic = random.choice(topics)
    
    # Dizayn qoidalari bo'yicha topikni ko'rsatish
    text = f"""
━━━━━━━━━━━━━━━━━━━━━━
🎤 {exam} Speaking — Part {topic[1]}
📊 Daraja: {topic[2]}
━━━━━━━━━━━━━━━━━━━━━━

📌 {topic[4]}

⏱️ Gapirish vaqti: {'1–2 daqiqa' if topic[1] == 2 else '30-60 soniya'}
━━━━━━━━━━━━━━━━━━━━━━
🎙 Gapirish uchun audio yuboring!
"""
    # Audio qabul qilish uchun topic_id ni stateda saqlash kerak, 
    # lekin hozircha oddiyroq yo'l: callback_data da saqlaymiz.
    await cb.message.edit_text(text, reply_markup=kb.kb(
        ("🔄 Boshqa topik", f"part_{part_id}_{exam}"),
        ("🏠 Menu", "menu")
    ))
