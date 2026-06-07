from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import config

# Async engine yaratamiz
engine = create_async_engine(
    config.database_url,
    echo=False,  # Loglarni o'chirish
    future=True
)

# Session factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_session() -> AsyncSession:
    """Yangi ma'lumotlar bazasi sessiyasini qaytaradi"""
    async with async_session() as session:
        yield session
