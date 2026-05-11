from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import ai, db
from keyboards import keyboards as kb
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
    await state.set_state(SpeakingStates.part1)
    
    # Randomly pick a Part 1 topic
    topics = ["Home and neighborhood", "Family and friends", "Work or study", "Daily routine", "Hobbies"]
    topic = random.choice(topics)
    
    await state.update_data(current_topic=topic, part=1, question_count=0, answers=[])
    
    msg = f"<b>{t('part1_intro', lang)}</b>\n\nTopic: {topic}\n\n"
    msg += "1. Please tell me about your home. Do you like living there? Why?"
    
    await cb.message.edit_text(msg, parse_mode="HTML")

@router.message(SpeakingStates.part1, F.voice)
async def handle_part1(message: Message, state: FSMContext, user):
    data = await state.get_data()
    lang = user['lang']
    q_count = data.get('question_count', 0)
    answers = data.get('answers', [])
    
    loading = await message.answer("⏳ ...")
    
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"voices/{file_id}.ogg"
    os.makedirs("voices", exist_ok=True)
    await message.bot.download_file(file.file_path, file_path)
    transcript = await ai.transcribe(file_path)
    os.remove(file_path)
    
    answers.append(transcript)
    q_count += 1
    
    if q_count < 3:
        # Next question
        questions = [
            "Who do you live with?",
            "What is your favorite room in your house?",
            "How long have you lived there?"
        ]
        await loading.edit_text(f"Great! {questions[q_count]}")
        await state.update_data(question_count=q_count, answers=answers)
    else:
        # Transition to Part 2
        await loading.delete()
        await state.set_state(SpeakingStates.part2_prep)
        
        # Interest-based topic for Part 2
        interests = user['interests'].split(",") if user['interests'] else ["travel"]
        topic = random.choice(interests)
        
        cue_card = f"<b>{t('part2_intro', lang)}</b>\n\n"
        cue_card += f"Topic: A memorable experience related to {topic}.\n"
        cue_card += "You should say:\n"
        cue_card += "• Where it was and who you were with\n"
        cue_card += "• What happened\n"
        cue_card += "• Why it was important or memorable\n\n"
        cue_card += f"<i>{t('prep_time_msg', lang)}</i>"
        
        await message.answer(cue_card, parse_mode="HTML", reply_markup=kb.prep_kb(lang))
        await state.update_data(p2_topic=topic)

@router.callback_query(SpeakingStates.part2_prep, F.data == "start_monologue")
async def start_monologue(cb: CallbackQuery, state: FSMContext, user):
    await state.set_state(SpeakingStates.part2_talk)
    await cb.message.edit_text("🎤 I'm listening! Please speak for 1-2 minutes.")

@router.message(SpeakingStates.part2_talk, F.voice)
async def handle_part2(message: Message, state: FSMContext, user):
    loading = await message.answer("⏳ Analyzing your monologue...")
    
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"voices/{file_id}.ogg"
    await message.bot.download_file(file.file_path, file_path)
    transcript = await ai.transcribe(file_path)
    os.remove(file_path)
    
    await loading.edit_text("🤖 Generating feedback for Part 2...")
    data = await state.get_data()
    res = await ai.get_feedback(transcript, data['p2_topic'], user['lang'], part=2)
    
    await message.answer(res['full_text'], parse_mode="HTML")
    
    # Transition to Part 3
    await state.set_state(SpeakingStates.part3)
    await state.update_data(p3_q_count=0)
    
    p3_intro = f"<b>{t('part3_intro', user['lang'])}</b>\n\n"
    p3_intro += f"Let's discuss more about {data['p2_topic']}.\n"
    p3_intro += "How has tourism changed in your country in the last ten years?"
    
    await message.answer(p3_intro, parse_mode="HTML")

@router.message(SpeakingStates.part3, F.voice)
async def handle_part3(message: Message, state: FSMContext, user):
    data = await state.get_data()
    q_count = data.get('p3_q_count', 0)
    
    loading = await message.answer("⏳ ...")
    
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"voices/{file_id}.ogg"
    await message.bot.download_file(file.file_path, file_path)
    transcript = await ai.transcribe(file_path)
    os.remove(file_path)
    
    q_count += 1
    
    if q_count < 3:
        questions = [
            "What are the pros and cons of international tourism?",
            "Do you think virtual reality will replace real travel in the future?"
        ]
        await loading.edit_text(questions[q_count-1])
        await state.update_data(p3_q_count=q_count)
    else:
        # Final evaluation
        await loading.edit_text("📊 <b>Generating final session results...</b>", parse_mode="HTML")
        
        # Use AI to summarize all parts (simplified here)
        res = await ai.get_feedback(transcript, "Discussion", user['lang'], part=3)
        
        # Save to DB
        db.save_result(user['tg_id'], 0, transcript, res['band'], res['cefr'], res['full_text'], res['grammar'], res['vocab'])
        
        await loading.edit_text(res['full_text'], parse_mode="HTML", reply_markup=kb.session_end_kb(user['lang']))
        await state.clear()
