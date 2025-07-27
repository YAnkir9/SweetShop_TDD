"""
Test configuration and fixtures for the Sweet Shop application
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, text
from app.main import app
from app.database import Base
from app.models import Role

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_data():
    """Set up test data once for the entire session"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create default role
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = select(Role).where(Role.name == "user")
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            role = Role(name="user")
            session.add(role)
            await session.commit()
    
    await engine.dispose()


@pytest.fixture(autouse=True)
async def cleanup_database():
    """Clean up database before each test to ensure test isolation"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Clean essential tables for test isolation
        tables_to_clean = [
            ("users", "users_id_seq"),
            ("revoked_tokens", "revoked_tokens_id_seq")
        ]
        
        for table, sequence in tables_to_clean:
            try:
                await conn.execute(text(f"DELETE FROM {table} WHERE id > 0"))
                await conn.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))
            except Exception:
                pass  # Table might not exist
    
    await engine.dispose()
    yield


@pytest.fixture
async def test_role():
    """Get the test role for use in tests"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with async_session() as session:
        stmt = select(Role).where(Role.name == "user")
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
    
    await engine.dispose()
    return role


@pytest.fixture
def client():
    """Provide test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client
