from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import config

def normalize_db_url(url: str) -> str:
    if not url:
        # fallback — lokal yoki Railway bo'lmasa SQLite ishlatish
        return "sqlite+aiosqlite:///./bot.db"
    # Railway yoki boshqadan kelgan `postgres://` ni asyncpg ga mos shaklga keltirish
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

DATABASE_URL = normalize_db_url(config.database_url)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
