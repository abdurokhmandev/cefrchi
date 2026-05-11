from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import db
import keyboards as kb

router = Router()

class Registration(StatesGroup):
    lang = State()
    full_name = State()
    level = State()
    exam = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user):
    if user:
        await message.answer(f"👋 Xush kelibsiz, {user['full_name']}!", reply_markup=kb.main_menu(user['lang']))
        return
    
    await state.set_state(Registration.lang)
    await message.answer("🌐 Tilni tanlang / Choose language:", reply_markup=kb.lang_kb())

@router.callback_query(Registration.lang)
async def reg_lang(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    await state.update_data(lang=lang)
    await state.set_state(Registration.full_name)
    text = "👤 To'liq ismingizni kiriting:" if lang == 'uz' else "👤 Enter your full name:"
    await cb.message.edit_text(text)

@router.message(Registration.full_name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    data = await state.get_data()
    lang = data['lang']
    await state.set_state(Registration.level)
    text = "📈 Ingliz tili darajangizni tanlang:" if lang == 'uz' else "📈 Choose your English level:"
    await message.answer(text, reply_markup=kb.level_kb())

@router.callback_query(Registration.level)
async def reg_level(cb: CallbackQuery, state: FSMContext):
    level = cb.data.split("_")[1]
    await state.update_data(level=level)
    data = await state.get_data()
    lang = data['lang']
    await state.set_state(Registration.exam)
    text = "🎯 Qaysi imtihonga tayyorlanyapsiz?" if lang == 'uz' else "🎯 Which exam are you preparing for?"
    await cb.message.edit_text(text, reply_markup=kb.exam_kb())

@router.callback_query(Registration.exam)
async def reg_exam(cb: CallbackQuery, state: FSMContext):
    exam = cb.data.split("_")[1]
    data = await state.get_data()
    lang = data['lang']
    
    db.add_user(cb.from_user.id, cb.from_user.username, data['full_name'], lang, data['level'], exam)
    await state.clear()
    
    welcome = f"""
╔══════════════════════╗
║  Xush kelibsiz, {data['full_name']}! ║
╚══════════════════════╝
📊 Daraja: {data['level']}
🎯 Imtihon: {exam}
🌐 Til: {'O\'zbek' if lang == 'uz' else 'English'}
"""
    await cb.message.edit_text(welcome, reply_markup=kb.main_menu(lang))
