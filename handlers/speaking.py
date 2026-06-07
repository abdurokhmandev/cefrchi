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
    from aiogram.types import Message as _Message
    if isinstance(msg_obj, _Message):
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
    if not isinstance(msg_obj, _Message): await status_msg.delete()
    await state.clear()
