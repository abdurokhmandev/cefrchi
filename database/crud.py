from sqlalchemy import select, update, delete, asc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
import uuid

from .models import User, Score, VocabCard, GrammarMistake, Session

# --- User CRUD ---
async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    """Foydalanuvchini ID bo'yicha olish"""
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, user_id: int, full_name: str, username: Optional[str] = None) -> User:
    """Yangi foydalanuvchi yaratish"""
    user = User(user_id=user_id, full_name=full_name, username=username)
    session.add(user)
    await session.commit()
    return user

async def update_user(session: AsyncSession, user_id: int, **kwargs):
    """Foydalanuvchi ma'lumotlarini yangilash"""
    stmt = update(User).where(User.user_id == user_id).values(**kwargs)
    await session.execute(stmt)
    await session.commit()

async def get_all_users(session: AsyncSession) -> List[User]:
    """Barcha foydalanuvchilarni olish (Eslatmalar uchun kerak bo'ladi)"""
    stmt = select(User)
    result = await session.execute(stmt)
    return list(result.scalars().all())

# --- Score CRUD ---
async def add_score(session: AsyncSession, user_id: int, skill: str, band_score: float, cefr_level: str, sub_scores: dict, feedback_uz: str, feedback_en: str, raw_input: str) -> Score:
    """Yangi natijani saqlash"""
    score = Score(
        user_id=user_id,
        skill=skill,
        band_score=band_score,
        cefr_level=cefr_level,
        sub_scores=sub_scores,
        feedback_uz=feedback_uz,
        feedback_en=feedback_en,
        raw_input=raw_input
    )
    session.add(score)
    await session.commit()
    return score

async def get_recent_scores(session: AsyncSession, user_id: int, limit: int = 5) -> List[Score]:
    """Foydalanuvchining so'nggi natijalarini olish"""
    stmt = select(Score).where(Score.user_id == user_id).order_by(Score.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())

# --- VocabCard CRUD ---
async def add_vocab_card(session: AsyncSession, user_id: int, word: str, def_uz: str, def_en: str, example: str) -> VocabCard:
    """Yangi so'z kartasini qo'shish"""
    card = VocabCard(
        user_id=user_id, 
        word=word, 
        definition_uz=def_uz, 
        definition_en=def_en, 
        example_sentence=example
    )
    session.add(card)
    await session.commit()
    return card

async def get_due_vocab_cards(session: AsyncSession, user_id: int, limit: int = 10) -> List[VocabCard]:
    """Takrorlash vaqti kelgan so'zlarni olish"""
    stmt = select(VocabCard).where(
        VocabCard.user_id == user_id, 
        VocabCard.next_review <= datetime.utcnow()
    ).order_by(asc(VocabCard.next_review)).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())

async def update_vocab_card(session: AsyncSession, card_id: uuid.UUID, **kwargs):
    """So'z kartasi holatini yangilash (SM-2 algoritmidan keyin)"""
    stmt = update(VocabCard).where(VocabCard.id == card_id).values(**kwargs)
    await session.execute(stmt)
    await session.commit()

# --- Session CRUD ---
async def create_study_session(session: AsyncSession, user_id: int, module_type: str, duration: int, xp: int, band: float = None) -> Session:
    """Mashg'ulot seansini saqlash"""
    study_session = Session(
        user_id=user_id,
        module_type=module_type,
        duration_seconds=duration,
        xp_earned=xp,
        band_score=band,
        completed=True
    )
    session.add(study_session)
    
    # Foydalanuvchiga XP qo'shish
    user = await get_user(session, user_id)
    if user:
        user.xp_total += xp
        user.last_activity = datetime.utcnow()
    
    await session.commit()
    return study_session
