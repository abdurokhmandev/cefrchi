<<<<<<< HEAD
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import db
from keyboards import keyboards as kb
from utils import ai
from utils.i18n import t
import os
import random
import asyncio

router = Router()

class SpeakingStates(StatesGroup):
    part1 = State()
    part2_prep = State()
    part2_talk = State()
    part3 = State()

@router.callback_query(F.data == "topic")
async def start_speaking(cb: CallbackQuery, state: FSMContext, user):
    lang = user['lang']
    
    # Bazadan Part 1 savollarini olish
    p1_topics = db.get_filtered_topics(user['exam'], 1, user['level'])
    if not p1_topics:
        await cb.answer("❌ Part 1 uchun savollar topilmadi. Admin hali savol qo'shmagan bo'lishi mumkin.", show_alert=True)
        return

    # 3 ta tasodifiy savolni tanlash (agar yetarli bo'lsa)
    selected_questions = random.sample(p1_topics, min(len(p1_topics), 3))
    q_texts = [q[4] for q in selected_questions]
    
    await state.set_state(SpeakingStates.part1)
    await state.update_data(
        questions=q_texts, 
        part=1, 
        current_q_idx=0, 
        answers=[], 
        exam=user['exam'], 
        level=user['level']
    )
    
    msg = f"<b>{t('part1_intro', lang)}</b>\n\n"
    msg += f"1. {q_texts[0]}"
    
    await cb.message.edit_text(msg, parse_mode="HTML")
    await cb.answer()

@router.message(SpeakingStates.part1, F.voice)
async def handle_part1(message: Message, state: FSMContext, user):
    data = await state.get_data()
    lang = user['lang']
    questions = data['questions']
    idx = data['current_q_idx']
    answers = data['answers']
    
    loading = await message.answer("⏳ ...")
    
    # Audio transkripsiya (oddiy holatda saqlamaymiz, faqat matnni olamiz)
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"voices/p1_{file_id}.ogg"
    os.makedirs("voices", exist_ok=True)
    await message.bot.download_file(file.file_path, file_path)
    transcript = await ai.transcribe(file_path)
    if os.path.exists(file_path): os.remove(file_path)
    
    answers.append({"q": questions[idx], "a": transcript})
    idx += 1
    
    if idx < len(questions):
        # Keyingi savol
        await loading.edit_text(f"Great! {questions[idx]}")
        await state.update_data(current_q_idx=idx, answers=answers)
    else:
        # Part 2 ga o'tish
        await loading.delete()
        
        p2_topics = db.get_filtered_topics(data['exam'], 2, data['level'])
        if not p2_topics:
            await message.answer("❌ Part 2 uchun savollar topilmadi. Test to'xtatildi.")
            await state.clear()
            return
            
        topic = random.choice(p2_topics)
        cue_card = f"<b>{t('part2_intro', lang)}</b>\n\n"
        cue_card += f"{topic[4]}\n\n"
        cue_card += f"<i>{t('prep_time_msg', lang)}</i>"
        
        await state.set_state(SpeakingStates.part2_prep)
        await state.update_data(p2_topic=topic[4], p2_id=topic[0], answers=answers)
        await message.answer(cue_card, parse_mode="HTML", reply_markup=kb.prep_kb(lang))

@router.callback_query(SpeakingStates.part2_prep, F.data == "start_monologue")
async def start_monologue(cb: CallbackQuery, state: FSMContext, user):
    await state.set_state(SpeakingStates.part2_talk)
    await cb.message.edit_text("🎤 I'm listening! Please speak for 1-2 minutes.")

@router.message(SpeakingStates.part2_talk, F.voice)
async def handle_part2(message: Message, state: FSMContext, user):
    loading = await message.answer("⏳ Analyzing your monologue...")
    data = await state.get_data()
    
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"voices/p2_{file_id}.ogg"
    await message.bot.download_file(file.file_path, file_path)
    transcript = await ai.transcribe(file_path)
    if os.path.exists(file_path): os.remove(file_path)
    
    data['answers'].append({"q": data['p2_topic'], "a": transcript})
    
    # Part 3 ga o'tish (Intro)
    p3_topics = db.get_filtered_topics(data['exam'], 3, data['level'])
    if not p3_topics:
        # Agar Part 3 bo'lmasa natijani chiqaramiz
        await finalize_session(message, state, user, transcript, data['p2_id'])
        return

    q3 = random.sample(p3_topics, min(len(p3_topics), 2))
    q3_texts = [q[4] for q in q3]
    
    await state.set_state(SpeakingStates.part3)
    await state.update_data(p3_questions=q3_texts, p3_idx=0, answers=data['answers'], p2_id=data['p2_id'])
    
    await loading.delete()
    msg = f"<b>{t('part3_intro', user['lang'])}</b>\n\n{q3_texts[0]}"
    await message.answer(msg, parse_mode="HTML")

@router.message(SpeakingStates.part3, F.voice)
async def handle_part3(message: Message, state: FSMContext, user):
    data = await state.get_data()
    questions = data['p3_questions']
    idx = data['p3_idx']
    
    loading = await message.answer("⏳ ...")
    
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"voices/p3_{file_id}.ogg"
    await message.bot.download_file(file.file_path, file_path)
    transcript = await ai.transcribe(file_path)
    if os.path.exists(file_path): os.remove(file_path)
    
    data['answers'].append({"q": questions[idx], "a": transcript})
    idx += 1
    
    if idx < len(questions):
        await loading.edit_text(f"Interesting! {questions[idx]}")
        await state.update_data(p3_idx=idx, answers=data['answers'])
    else:
        await finalize_session(loading, state, user, transcript, data['p2_id'])

async def finalize_session(msg_obj, state, user, last_transcript, topic_id):
    # msg_obj ham Message ham Loading Message bo'lishi mumkin
    if isinstance(msg_obj, Message):
        status_msg = await msg_obj.answer("📊 <b>Generating final results...</b>", parse_mode="HTML")
    else:
        await msg_obj.edit_text("📊 <b>Generating final results...</b>", parse_mode="HTML")
        status_msg = msg_obj

    data = await state.get_data()
    full_transcript = "\n".join([f"Q: {ans['q']}\nA: {ans['a']}" for ans in data['answers']])
    
    # AI Feedback
    res = await ai.get_feedback(full_transcript, "Full Speaking Session", user['lang'], part=123)
    
    # Save to DB
    db.save_result(user['tg_id'], topic_id, full_transcript, res['band'], res['cefr'], res['full_text'], res['grammar'], res['vocab'])
    
    await status_msg.answer(res['full_text'], parse_mode="HTML", reply_markup=kb.session_end_kb(user['lang']))
    if not isinstance(msg_obj, Message): await status_msg.delete()
    await state.clear()
=======
import os
import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.whisper_stt import transcribe_audio
from services.openrouter import generate_speaking_question, grade_speaking
from locales.i18n import i18n
from keyboards.menus import get_speaking_parts_menu, get_speaking_result_menu
from database.engine import get_session
from database.crud import add_score, create_study_session

logger = logging.getLogger(__name__)
router = Router()

class SpeakingStates(StatesGroup):
    choosing_part = State()
    choosing_topic = State()
    preparing = State()
    recording = State()
    processing = State()

@router.callback_query(F.data == "menu_speaking")
async def start_speaking(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(i18n.get("speaking_start"), reply_markup=get_speaking_parts_menu())
    await state.set_state(SpeakingStates.choosing_part)

@router.callback_query(SpeakingStates.choosing_part, F.data.startswith("speak_part_"))
async def part_selected(callback: types.CallbackQuery, state: FSMContext):
    part = int(callback.data.split("_")[2])
    await state.update_data(part=part)
    
    try:
        await callback.message.edit_text("⏳ Savol tayyorlanmoqda...")
        q_data = await generate_speaking_question("B2", part)
        question = q_data.get("question", "Tell me about your hometown.")
        await state.update_data(question=question)
        
        text = i18n.get("speak_part_selected", part=part, question=question)
        
        if part == 2:
            await callback.message.edit_text(text + "\n\n" + i18n.get("speak_part2_prep"))
        else:
            await callback.message.edit_text(text)
            
        await state.set_state(SpeakingStates.recording)
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        await callback.message.edit_text("Savol yaratishda xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")

@router.message(SpeakingStates.recording, F.voice)
async def process_audio(message: types.Message, state: FSMContext, bot: Bot):
    await state.set_state(SpeakingStates.processing)
    wait_msg = await message.answer(i18n.get("speak_analyzing"))
    
    try:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = f"downloads/{file_id}.ogg"
        
        os.makedirs("downloads", exist_ok=True)
        await bot.download_file(file.file_path, destination=file_path)
        
        # Whisper STT orqali matnga o'girish
        transcript = await transcribe_audio(file_path)
        
        # OpenRouter orqali grading qilish
        data = await state.get_data()
        part = data.get("part", 1)
        question = data.get("question", "")
        
        grade = await grade_speaking(transcript, question, part)
        
        # Javobni formatlash
        strengths = "\n- ".join(grade.get("strengths", []))
        if strengths: strengths = "- " + strengths
            
        improvements = "\n- ".join(grade.get("improvements", []))
        if improvements: improvements = "- " + improvements
        
        result_text = i18n.get(
            "speak_result",
            band=grade.get("overall", 0.0),
            cefr=grade.get("cefr", "A2"),
            fluency=grade.get("fluency", 0.0),
            lexical=grade.get("lexical", 0.0),
            grammar=grade.get("grammar", 0.0),
            pronunciation=grade.get("pronunciation", 0.0),
            feedback_uz=grade.get("feedback_uz", "Ma'lumot topilmadi."),
            strengths=strengths,
            improvements=improvements,
            corrected_sample=grade.get("corrected_sample", "")
        )
        
        # Ma'lumotlarni bazaga saqlash
        async for session in get_session():
            await add_score(
                session, 
                message.from_user.id, 
                "speaking", 
                grade.get("overall", 0.0),
                grade.get("cefr", "A2"),
                grade, 
                grade.get("feedback_uz", ""), 
                "", 
                transcript
            )
            await create_study_session(
                session, 
                message.from_user.id, 
                "speaking", 
                120, 
                int(grade.get("overall", 0.0)*10), 
                grade.get("overall", 0.0)
            )
        
        await wait_msg.delete()
        await message.answer(result_text, reply_markup=get_speaking_result_menu())
        
        # Faylni o'chirish
        try:
            os.remove(file_path)
        except OSError:
            pass
            
        await state.clear()
        
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        await wait_msg.delete()
        await message.answer(i18n.get("speak_error"))
        await state.set_state(SpeakingStates.recording)

@router.callback_query(F.data == "speak_retry")
async def retry_speaking(callback: types.CallbackQuery, state: FSMContext):
    await start_speaking(callback, state)

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    from keyboards.menus import get_main_menu
    await callback.message.edit_text(i18n.get("main_menu"), reply_markup=get_main_menu())
>>>>>>> 1d2f1c3 (Initial commit)
