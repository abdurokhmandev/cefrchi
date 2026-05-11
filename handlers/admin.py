from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_IDS
import db
import keyboards as kb

router = Router()

class AdminStates(StatesGroup):
    broadcast = State()
    topic_text = State()
    topic_part = State()
    topic_exam = State()
    topic_level = State()

def admin_kb(*buttons):
    b = InlineKeyboardBuilder()
    for text, data in buttons:
        b.button(text=text, callback_data=data)
    b.adjust(2)
    return b.as_markup()

from aiogram.types import WebAppInfo
from config import ADMIN_IDS, WEBAPP_URL

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    total, tests, avg = db.get_stats()
    text = f"👑 <b>ADMIN PANEL</b>\n━━━━━━━━━━━━━━━━━━━━━━\n👥 Foydalanuvchilar: {total}\n🎤 Testlar: {tests}\n📊 O'rtacha: {avg:.1f}\n━━━━━━━━━━━━━━━━━━━━━━\n\n<i>Pastdagi tugma orqali interaktiv dashboardni ochishingiz mumkin.</i>"
    
    b = InlineKeyboardBuilder()
    b.button(text="🌐 Web Dashboard", web_app=WebAppInfo(url=WEBAPP_URL))
    b.button(text="📨 Xabar yuborish", callback_data="a_broadcast")
    b.button(text="➕ Topik qo'shish", callback_data="a_add_topic")
    b.button(text="📊 Statistika", callback_data="a_stats")
    b.adjust(1, 2)
    
    await message.answer(text, parse_mode="HTML", reply_markup=b.as_markup())


@router.callback_query(F.data == "a_add_topic")
async def add_topic_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.topic_exam)
    await cb.message.edit_text("🎯 Imtihon turini tanlang:", reply_markup=admin_kb(
        ("IELTS", "a_exam_IELTS"), ("CEFR", "a_exam_CEFR"), ("Ikkalasi", "a_exam_ALL")
    ))

@router.callback_query(AdminStates.topic_exam)
async def add_topic_exam(cb: CallbackQuery, state: FSMContext):
    exam = cb.data.split("_")[-1]
    await state.update_data(exam=exam)
    await state.set_state(AdminStates.topic_part)
    await cb.message.edit_text("🎤 Partni tanlang:", reply_markup=admin_kb(
        ("Part 1", "a_part_1"), ("Part 2", "a_part_2"), ("Part 3", "a_part_3")
    ))

@router.callback_query(AdminStates.topic_part)
async def add_topic_part(cb: CallbackQuery, state: FSMContext):
    part = int(cb.data.split("_")[-1])
    await state.update_data(part=part)
    await state.set_state(AdminStates.topic_level)
    await cb.message.edit_text("📈 Darajani tanlang:", reply_markup=admin_kb(
        ("A1", "a_lvl_A1"), ("A2", "a_lvl_A2"), ("B1", "a_lvl_B1"),
        ("B2", "a_lvl_B2"), ("C1", "a_lvl_C1"), ("C2", "a_lvl_C2"), ("ALL", "a_lvl_ALL")
    ))

@router.callback_query(AdminStates.topic_level)
async def add_topic_level(cb: CallbackQuery, state: FSMContext):
    level = cb.data.split("_")[-1]
    await state.update_data(level=level)
    data = await state.get_data()
    await state.set_state(AdminStates.topic_text)
    
    if data['part'] == 2:
        text = "📝 <b>Cue Card (Part 2) matnini kiriting:</b>"
    else:
        text = "📝 <b>Savollar ro'yxatini kiriting:</b>\n(Har bir savolni yangi qatordan yozing)"
    await cb.message.edit_text(text, parse_mode="HTML")

@router.message(AdminStates.topic_text)
async def add_topic_final(message: Message, state: FSMContext):
    data = await state.get_data()
    db.add_topic(data['part'], data['level'], data['exam'], message.text, message.from_user.id)
    await state.clear()
    await message.answer(f"✅ <b>Yangi topik qo'shildi!</b>\n\n📝 Tarkib:\n{message.text}", parse_mode="HTML")
