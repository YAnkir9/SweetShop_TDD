from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import logging
from .config import settings





class Base(DeclarativeBase):
    pass


def get_async_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def get_database_url() -> str:
    return get_async_database_url(settings.DATABASE_URL)


SQLALCHEMY_DATABASE_URL = get_database_url()

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=1,
    max_overflow=0,
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = None
    try:
        session = async_session()
        # session created
        yield session
        await session.commit()
        # session committed
    except Exception as e:
        if session:
            await session.rollback()
            # session rolled back due to error
        raise
    finally:
        if session:
            await session.close()
            # session closed


async def get_db_with_retry() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session with retry logic for better connectivity
    """
    max_retries = 3
    retry_delay = 1.0
    
    for attempt in range(max_retries):
        session = None
        try:
            session = async_session()
            # Test the connection with a simple query
            await session.execute("SELECT 1")
            
            try:
                yield session
                await session.commit()
                break
            except Exception as e:
                await session.rollback()
                # session error on attempt
                raise
            finally:
                if session:
                    await session.close()
                
        except Exception as e:
            if attempt == max_retries - 1:
                # all db connection attempts failed
                raise
            
            import asyncio
            # connection attempt failed, retrying
            await asyncio.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff


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
