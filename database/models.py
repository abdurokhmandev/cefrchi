import uuid
from datetime import datetime, date
from typing import Optional, Any
from sqlalchemy import (
    BigInteger, String, Float, Integer, Boolean, DateTime, Date, 
    Text, Enum, JSON, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(Enum('uz', 'ru', 'en', name='lang_enum'), default='uz')
    cefr_level: Mapped[str] = mapped_column(Enum('A1', 'A2', 'B1', 'B2', 'C1', 'C2', name='cefr_enum'), default='A2')
    target_band: Mapped[float] = mapped_column(Float, default=6.0)
    exam_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    xp_total: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    achievements: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True) # Badge lar uchun JSON field

    # Relationships
    scores: Mapped[list["Score"]] = relationship("Score", back_populates="user", cascade="all, delete-orphan")
    vocab_cards: Mapped[list["VocabCard"]] = relationship("VocabCard", back_populates="user", cascade="all, delete-orphan")
    grammar_mistakes: Mapped[list["GrammarMistake"]] = relationship("GrammarMistake", back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Score(Base):
    __tablename__ = "scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    skill: Mapped[str] = mapped_column(Enum('speaking', 'writing', 'reading', 'listening', 'overall', name='skill_enum'))
    band_score: Mapped[float] = mapped_column(Float)
    cefr_level: Mapped[str] = mapped_column(String)
    sub_scores: Mapped[Any] = mapped_column(JSON)
    feedback_uz: Mapped[str] = mapped_column(Text)
    feedback_en: Mapped[str] = mapped_column(Text)
    raw_input: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="scores")

class VocabCard(Base):
    __tablename__ = "vocab_cards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    word: Mapped[str] = mapped_column(String)
    definition_uz: Mapped[str] = mapped_column(Text)
    definition_en: Mapped[str] = mapped_column(Text)
    example_sentence: Mapped[str] = mapped_column(Text)
    next_review: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    interval_days: Mapped[float] = mapped_column(Float, default=1.0)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    is_learned: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="vocab_cards")

class GrammarMistake(Base):
    __tablename__ = "grammar_mistakes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    topic: Mapped[str] = mapped_column(String)
    mistake_text: Mapped[str] = mapped_column(Text)
    correction: Mapped[str] = mapped_column(Text)
    explanation_uz: Mapped[str] = mapped_column(Text)
    count: Mapped[int] = mapped_column(Integer, default=1)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="grammar_mistakes")

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    module_type: Mapped[str] = mapped_column(Enum('speaking', 'writing', 'reading', 'listening', 'vocab', 'grammar', 'mock', name='module_enum'))
    duration_seconds: Mapped[int] = mapped_column(Integer)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    band_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="sessions")
