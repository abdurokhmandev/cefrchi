<<<<<<< HEAD
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import db, ai
from keyboards import keyboards as kb
from utils.i18n import t
from config import ADMIN_IDS
import os

router = Router()

class Registration(StatesGroup):
    lang = State()
    full_name = State()
    age = State()
    interests = State()
    level = State()
    level_test = State()
    exam = State()
    source = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user):
    user_id = message.from_user.id
    
    # Agar foydalanuvchi bazada bo'lsa
    if user:
        welcome = t('main_menu_msg', user['lang'], name=user['full_name'])
        await message.answer(welcome, reply_markup=kb.main_menu(user['lang']))
        return

    # Agar foydalanuvchi bazada bo'lmasa-yu, lekin ADMIN bo'lsa
    if user_id in ADMIN_IDS:
        # Adminni foydalanuvchi sifatida ham vaqtincha bazaga qo'shib qo'yamiz (agar xohlasa ro'yxatdan o'tadi)
        # Lekin hozircha unga menyuni ko'rsatamiz
        await message.answer("Xush kelibsiz, Admin! 👑\nSiz ro'yxatdan o'tmagansiz, lekin admin huquqingiz bor.", reply_markup=kb.main_menu('uz'))
        return
    
    # Yangi foydalanuvchi uchun ro'yxatdan o'tish
    await state.clear()
    msg = await message.answer(t('welcome', 'uz'), reply_markup=kb.start_kb('uz'))
    await state.update_data(msg_ids=[msg.message_id])

@router.callback_query(F.data == "register")
async def start_reg(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.lang)
    await cb.message.edit_text(t('step_lang', 'uz'), reply_markup=kb.lang_kb())

@router.callback_query(Registration.lang, F.data.startswith("lang_"))
async def reg_lang(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    await state.update_data(lang=lang)
    await state.set_state(Registration.full_name)
    await cb.message.edit_text(t('step_name', lang))

@router.message(Registration.full_name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    data = await state.get_data()
    lang = data['lang']
    msg_ids = data.get('msg_ids', [])
    msg_ids.append(message.message_id)
    
    await state.set_state(Registration.age)
    msg = await message.answer(t('step_age', lang))
    msg_ids.append(msg.message_id)
    await state.update_data(msg_ids=msg_ids)

@router.message(Registration.age)
async def reg_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, raqam kiriting:")
        return
    
    await state.update_data(age=int(message.text))
    data = await state.get_data()
    lang = data['lang']
    msg_ids = data.get('msg_ids', [])
    msg_ids.append(message.message_id)
    
    await state.set_state(Registration.interests)
    msg = await message.answer(t('step_interests', lang), reply_markup=kb.interests_kb(lang))
    msg_ids.append(msg.message_id)
    await state.update_data(msg_ids=msg_ids, selected_interests=[])

@router.callback_query(Registration.interests, F.data.startswith("interest_"))
async def reg_interests(cb: CallbackQuery, state: FSMContext):
    code = cb.data.split("_")[1]
    data = await state.get_data()
    lang = data['lang']
    selected = data.get('selected_interests', [])
    
    if code == "ready":
        if not selected:
            await cb.answer("Kamida bittasini tanlang", show_alert=True)
            return
        await state.set_state(Registration.level)
        await cb.message.edit_text(t('step_level', lang), reply_markup=kb.level_kb(lang))
        return

    if code in selected: selected.remove(code)
    else: selected.append(code)
    
    await state.update_data(selected_interests=selected)
    await cb.message.edit_reply_markup(reply_markup=kb.interests_kb(lang, selected))

@router.callback_query(Registration.level, F.data.startswith("level_"))
async def reg_level(cb: CallbackQuery, state: FSMContext):
    level = cb.data.split("_")[1]
    data = await state.get_data()
    lang = data['lang']
    
    if level == "unknown":
        await state.set_state(Registration.level_test)
        await state.update_data(test_step=0, test_answers=[])
        await cb.message.edit_text(t('level_test_start', lang))
        msg = await cb.message.answer("1. Tell me about your hometown.")
        data['msg_ids'].append(msg.message_id)
        await state.update_data(msg_ids=data['msg_ids'])
        return

    await state.update_data(level=level)
    await state.set_state(Registration.exam)
    await cb.message.edit_text(t('step_exam', lang), reply_markup=kb.exam_kb(lang))

@router.message(Registration.level_test, F.voice)
async def reg_level_test(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    step = data.get('test_step', 0)
    answers = data.get('test_answers', [])
    msg_ids = data.get('msg_ids', [])
    msg_ids.append(message.message_id)

    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"voices/test_{file_id}.ogg"
    os.makedirs("voices", exist_ok=True)
    await message.bot.download_file(file.file_path, file_path)
    transcript = await ai.transcribe(file_path)
    os.remove(file_path)
    
    answers.append(transcript)
    step += 1
    
    if step < 3:
        questions = ["1. Tell me about your hometown.", "2. What do you like to do in your free time?", "3. Why do you want to learn English?"]
        msg = await message.answer(f"{step+1}. {questions[step]}")
        msg_ids.append(msg.message_id)
        await state.update_data(test_step=step, test_answers=answers, msg_ids=msg_ids)
    else:
        wait_msg = await message.answer("⏳ Processing...")
        msg_ids.append(wait_msg.message_id)
        detected_level = await ai.detect_level(answers)
        await wait_msg.edit_text(t('level_result', lang, level=detected_level))
        
        await state.update_data(level=detected_level, msg_ids=msg_ids)
        await state.set_state(Registration.exam)
        msg = await message.answer(t('step_exam', lang), reply_markup=kb.exam_kb(lang))
        msg_ids.append(msg.message_id)
        await state.update_data(msg_ids=msg_ids)

@router.callback_query(Registration.exam, F.data.startswith("exam_"))
async def reg_exam(cb: CallbackQuery, state: FSMContext):
    exam = cb.data.split("_")[1]
    await state.update_data(exam=exam)
    data = await state.get_data()
    lang = data['lang']
    await state.set_state(Registration.source)
    await cb.message.edit_text(t('step_source', lang), reply_markup=kb.source_kb(lang))

@router.callback_query(Registration.source, F.data.startswith("source_"))
async def reg_source(cb: CallbackQuery, state: FSMContext):
    source = cb.data.split("_")[1]
    data = await state.get_data()
    lang = data['lang']
    
    # Bazaga saqlash
    interests_str = ",".join(data['selected_interests'])
    db.add_user(
        cb.from_user.id, cb.from_user.username, data['full_name'], 
        lang, data['age'], interests_str, data['level'], 
        data['exam'], source
    )
    
    # Xabarlarni tozalash
    msg_ids = data.get('msg_ids', [])
    for msg_id in msg_ids:
        try: await cb.bot.delete_message(cb.message.chat.id, msg_id)
        except: pass
            
    await state.clear()
    
    # Menyu ko'rsatish
    welcome = t('reg_done', lang) + "\n\n" + t('main_menu_msg', lang, name=data['full_name'])
    await cb.message.answer(welcome, reply_markup=kb.main_menu(lang))
=======
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from datetime import datetime

from database.engine import get_session
from database.crud import get_user, create_user, update_user
from locales.i18n import i18n
from keyboards.menus import get_target_band_menu, get_main_menu

router = Router()

class OnboardingStates(StatesGroup):
    testing = State()
    exam_date = State()
    target_band = State()

# Placement test savollari (Soddalashtirilgan)
PLACEMENT_QUESTIONS = [
    {"q": "1. She _____ to the store yesterday.", "opts": ["go", "goes", "went", "gone"], "ans": "went"},
    {"q": "2. I have _____ living here for 5 years.", "opts": ["be", "been", "being", "was"], "ans": "been"},
    {"q": "3. The movie was very _____, I fell asleep.", "opts": ["boring", "bored", "bore", "bores"], "ans": "boring"},
    {"q": "4. Synonym for 'Happy':", "opts": ["Sad", "Angry", "Joyful", "Tired"], "ans": "Joyful"},
    {"q": "5. Antonym of 'Difficult':", "opts": ["Hard", "Complex", "Easy", "Tough"], "ans": "Easy"}
]

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    async for session in get_session():
        user = await get_user(session, user_id)
        if not user:
            # Yangi foydalanuvchini DB ga qo'shish
            await create_user(session, user_id, message.from_user.full_name, message.from_user.username)
            await message.answer(i18n.get("welcome", name=message.from_user.first_name))
            
            # Placement testni boshlash
            await state.update_data(score=0, q_index=0)
            await ask_question(message, state)
            return

        # Eski foydalanuvchi bo'lsa, to'g'ridan-to'g'ri menyuga yuboramiz
        await message.answer(i18n.get("main_menu"), reply_markup=get_main_menu())

async def ask_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    idx = data.get("q_index", 0)
    
    if idx >= len(PLACEMENT_QUESTIONS):
        # Natija hisoblash logikasi
        score = data.get("score", 0)
        cefr = "A1"
        band = "3.0"
        if score == 5:
            cefr, band = "B1", "5.0"
        elif score >= 3:
            cefr, band = "A2", "4.0"
            
        await state.update_data(cefr=cefr)
        await message.answer(i18n.get("placement_result", cefr=cefr, band=band), reply_markup=ReplyKeyboardRemove())
        await state.set_state(OnboardingStates.exam_date)
        return

    q_data = PLACEMENT_QUESTIONS[idx]
    
    # Variantlarni tugma qilib chiqaramiz
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=opt)] for opt in q_data["opts"]],
        resize_keyboard=True
    )
    
    await message.answer(q_data["q"], reply_markup=kb)
    await state.set_state(OnboardingStates.testing)

@router.message(OnboardingStates.testing)
async def check_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    idx = data.get("q_index", 0)
    q_data = PLACEMENT_QUESTIONS[idx]
    
    # Agar foydalanuvchi to'g'ri javob bersa
    if message.text == q_data["ans"]:
        await state.update_data(score=data.get("score", 0) + 1)
        
    await state.update_data(q_index=idx + 1)
    await ask_question(message, state)

@router.message(OnboardingStates.exam_date)
async def process_exam_date(message: types.Message, state: FSMContext):
    date_str = message.text
    
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        await state.update_data(exam_date=parsed_date)
        
        await message.answer(i18n.get("exam_date_saved"))
        await message.answer("Maqsad bandni tanlang:", reply_markup=get_target_band_menu())
        await state.set_state(OnboardingStates.target_band)
    except ValueError:
        await message.answer("Sana formati xato! Iltimos, YYYY-MM-DD shaklida kiriting (Masalan: 2024-12-31).")

@router.callback_query(OnboardingStates.target_band, F.data.startswith("target_"))
async def process_target_band(callback: types.CallbackQuery, state: FSMContext):
    band = float(callback.data.split("_")[1])
    data = await state.get_data()
    cefr = data.get("cefr", "A2")
    exam_date = data.get("exam_date")
    
    async for session in get_session():
        await update_user(
            session, 
            callback.from_user.id, 
            cefr_level=cefr, 
            target_band=band,
            exam_date=exam_date
        )

    await callback.message.edit_text(i18n.get("target_saved"))
    await callback.message.answer(i18n.get("main_menu"), reply_markup=get_main_menu())
    await state.clear()
>>>>>>> 1d2f1c3 (Initial commit)
