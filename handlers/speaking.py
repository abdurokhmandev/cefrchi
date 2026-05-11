from aiogram import Router, F
from aiogram.types import Message
import os
import ai
import db
import keyboards as kb

router = Router()

@router.message(F.voice)
async def handle_voice(message: Message, user):
    if not user: return

    loading_msg = await message.answer("⏳ <b>Audio tahlil qilinmoqda...</b>", parse_mode="HTML")
    
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"voices/{file_id}.ogg"
    os.makedirs("voices", exist_ok=True)
    await message.bot.download_file(file.file_path, file_path)

    # Transcript
    transcript = await ai.transcribe(file_path)
    if not transcript:
        await loading_msg.edit_text("❌ Audioni tahlil qilib bo'lmadi. Qayta urinib ko'ring.")
        os.remove(file_path)
        return

    await loading_msg.edit_text("🤖 <b>Feedback tayyorlanmoqda...</b>", parse_mode="HTML")
    
    # Feedback
    res = await ai.get_feedback(transcript, "IELTS Speaking Topic", user['lang'])
    
    if "error" in res:
        await loading_msg.edit_text(f"❌ {res['feedback']}")
        os.remove(file_path)
        return

    # DB ga saqlash
    db.save_result(
        user['tg_id'], 0, transcript, 
        res['band'], res['cefr'], res['full_text'], 
        res['grammar'], res['vocab']
    )

    # Natijani ko'rsatish
    final_text = f"""
━━━━━━━━━━━━━━━━━━━━━━
📝 <b>Sizning javobingiz:</b>
━━━━━━━━━━━━━━━━━━━━━━
"{transcript}"

━━━━━━━━━━━━━━━━━━━━━━
📊 <b>BAHOLASH NATIJALARI</b>
━━━━━━━━━━━━━━━━━━━━━━
{res['full_text']}

━━━━━━━━━━━━━━━━━━━━━━
✍️ <b>Grammatika va Lug'at:</b>
━━━━━━━━━━━━━━━━━━━━━━
<b>Grammatika:</b>
{res['grammar'] or "Ajoyib! Jiddiy xatolar yo'q."}

<b>Lug'at (Vocabulary):</b>
{res['vocab'] or "So'z boyligi yetarli darajada."}
━━━━━━━━━━━━━━━━━━━━━━
"""
    await loading_msg.edit_text(final_text, parse_mode="HTML", reply_markup=kb.kb(
        ("🎤 Yangi topik", "topic"),
        ("📊 Natijalarim", "history_0")
    ))

    
    os.remove(file_path)
