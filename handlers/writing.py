import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.openrouter import grade_writing
from locales.i18n import i18n
from database.engine import get_session
from database.crud import add_score, create_study_session

logger = logging.getLogger(__name__)
router = Router()

class WritingStates(StatesGroup):
    writing_essay = State()
    processing = State()

@router.callback_query(F.data == "menu_writing")
async def start_writing(callback: types.CallbackQuery, state: FSMContext):
    # Dastlab Task 2 sifatida olamiz, aslida Task tanlash menyusi ham qo'shish mumkin
    await state.update_data(task_type="Task 2", prompt="Some people believe that university education should be free for everyone. To what extent do you agree or disagree?")
    
    await callback.message.edit_text("✍️ IELTS Writing Task 2\n\nPrompt: Some people believe that university education should be free for everyone. To what extent do you agree or disagree?\n\nIltimos, essengizni yuboring (Kamida 250 so'z).")
    await state.set_state(WritingStates.writing_essay)

@router.message(WritingStates.writing_essay, F.text)
async def process_essay(message: types.Message, state: FSMContext):
    await state.set_state(WritingStates.processing)
    wait_msg = await message.answer("⏳ Essengiz tekshirilmoqda...")
    
    try:
        data = await state.get_data()
        essay = message.text
        
        grade = await grade_writing(essay, data.get("task_type"), data.get("prompt"))
        
        grammar_errors = ""
        for err in grade.get("grammar_errors", []):
            grammar_errors += f"- Xato: {err.get('wrong')} -> To'g'ri: {err.get('correct')} ({err.get('rule')})\n"
            
        vocab_suggs = ""
        for sugg in grade.get("vocab_suggestions", []):
            vocab_suggs += f"- {sugg.get('used')} -> {sugg.get('better')}\n"
            
        result_text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✍️ Writing natijasi\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Band score: {grade.get('overall', 0.0)}\n"
            f"🎓 CEFR: {grade.get('cefr', 'B2')}\n\n"
            f"Task Response: {grade.get('criterion1', grade.get('task_response', 0.0))} ⭐️\n"
            f"Coherence:     {grade.get('criterion2', grade.get('coherence', 0.0))} ⭐️\n"
            f"Vocabulary:    {grade.get('lexical', 0.0)} ⭐️\n"
            f"Grammar:       {grade.get('grammar', 0.0)} ⭐️\n\n"
            f"💬 Baho:\n{grade.get('feedback_uz', '')}\n\n"
            f"📝 Grammatika xatolaringiz:\n{grammar_errors}\n"
            f"📚 So'z boyligi bo'yicha maslahatlar:\n{vocab_suggs}\n"
            f"💡 Struktura: {grade.get('structure_feedback', '')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        # Ma'lumotlarni bazaga saqlash
        async for session in get_session():
            await add_score(
                session, 
                message.from_user.id, 
                "writing", 
                grade.get("overall", 0.0),
                grade.get("cefr", "A2"),
                grade, 
                grade.get("feedback_uz", ""), 
                "", 
                essay
            )
            await create_study_session(
                session, 
                message.from_user.id, 
                "writing", 
                3600, 
                int(grade.get("overall", 0.0)*15), 
                grade.get("overall", 0.0)
            )

        await wait_msg.delete()
        
        from keyboards.menus import get_back_menu
        await message.answer(result_text, reply_markup=get_back_menu())
        await state.clear()

    except Exception as e:
        logger.error(f"Error checking essay: {e}")
        await wait_msg.delete()
        await message.answer("Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
        await state.set_state(WritingStates.writing_essay)
