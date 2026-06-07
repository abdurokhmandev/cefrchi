import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.engine import get_session
from database.crud import get_due_vocab_cards, update_vocab_card, add_vocab_card
from services.srs import calculate_next_review

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "menu_vocab")
async def start_vocab(callback: types.CallbackQuery):
    async for session in get_session():
        due_cards = await get_due_vocab_cards(session, callback.from_user.id, limit=1)
        
        if not due_cards:
            # Agar qaytaradigan kartalar qolmagan bo'lsa (namuna sifatida yangi so'z qo'shamiz)
            await add_vocab_card(
                session, 
                callback.from_user.id, 
                "Ubiquitous", 
                "Hamma joyda mavjud", 
                "Present, appearing, or found everywhere", 
                "His ubiquitous influence was felt by all the family."
            )
            due_cards = await get_due_vocab_cards(session, callback.from_user.id, limit=1)
            if not due_cards:
                await callback.message.edit_text("Hozircha barcha so'zlarni takrorladingiz! Keyinroq yana tekshiring.")
                return
                
        card = due_cards[0]
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Qiyin (Again)", callback_data=f"vocab_1_{card.id}"),
                InlineKeyboardButton(text="Yaxshi (Good)", callback_data=f"vocab_3_{card.id}")
            ],
            [
                InlineKeyboardButton(text="Oson (Easy)", callback_data=f"vocab_5_{card.id}"),
                InlineKeyboardButton(text="🏠 Menyu", callback_data="back_to_main")
            ]
        ])
        
        text = (
            f"📚 Vocabulary\n\n"
            f"So'z: **{card.word}**\n\n"
            f"🇬🇧 {card.definition_en}\n"
            f"🇺🇿 {card.definition_uz}\n\n"
            f"📝 Example: {card.example_sentence}"
        )
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)

@router.callback_query(F.data.startswith("vocab_"))
async def process_vocab_answer(callback: types.CallbackQuery):
    _, quality_str, card_id = callback.data.split("_")
    quality = int(quality_str)
    
    async for session in get_session():
        # Kartani olish
        from database.models import VocabCard
        from sqlalchemy import select
        card = await session.scalar(select(VocabCard).where(VocabCard.id == card_id))
        
        if card:
            # SM-2 hisoblash
            res = calculate_next_review(quality, card.repetitions, card.ease_factor, card.interval_days)
            
            await update_vocab_card(
                session, 
                card.id, 
                next_review=res["next_date"],
                interval_days=res["new_interval"],
                ease_factor=res["new_ease_factor"],
                repetitions=res["new_repetitions"]
            )
            
            # Keyingi kartani ko'rsatish
            await start_vocab(callback)
            return

    await callback.answer("Karta topilmadi.")
