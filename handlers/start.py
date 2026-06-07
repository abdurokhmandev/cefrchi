from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import db
from keyboards import keyboards as kb
from utils import ai
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
async def cmd_start(message: Message, state: FSMContext, user=None):
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
