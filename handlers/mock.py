import asyncio
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from locales.i18n import i18n
from keyboards.menus import get_back_menu

router = Router()

class MockExamStates(StatesGroup):
    listening = State()
    reading = State()
    writing = State()
    speaking = State()
    result = State()

@router.callback_query(F.data == "menu_mock")
async def start_mock_exam(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📋 Mock Imtihon boshlanmoqda.\n\n"
        "Imtihon tartibi:\n"
        "1. Listening (30 daqiqa)\n"
        "2. Reading (60 daqiqa)\n"
        "3. Writing (60 daqiqa)\n"
        "4. Speaking (15 daqiqa)\n\n"
        "Tayyormisiz? (Hozircha simulyatsiya qilinadi)",
        reply_markup=get_back_menu()
    )
    # Bu yerda to'liq mock exam flow implementatsiya qilinadi.
