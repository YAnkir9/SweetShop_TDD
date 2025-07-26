from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from .config import settings


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


def get_async_database_url(url: str) -> str:
    """Convert sync PostgreSQL URL to async URL"""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


SQLALCHEMY_DATABASE_URL = get_async_database_url(settings.DATABASE_URL)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency that provides database session.
    Automatically handles session cleanup and rollback on errors.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all database tables and triggers"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    from .triggers import create_triggers
    await create_triggers()


async def drop_tables():
    """Drop all database tables and triggers (for testing)"""
    from .triggers import drop_triggers
    await drop_triggers()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db():
    """Close database engine (for shutdown)"""
    await engine.dispose()
