import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.main import app
from app.database import get_db, Base
from app.models import Role


# Use same database as main for simplicity in TDD
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Provide sync test client for testing"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def test_role():
    """Create a test role for auth tests"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if role already exists
        stmt = select(Role).where(Role.name == "user")
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            role = Role(name="user")
            session.add(role)
            await session.commit()
            await session.refresh(role)
    
    await engine.dispose()
    return role
from app.database import get_db, Base
from app.models import Role


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture
async def test_db():
    """Create a test database"""
    # Use in-memory SQLite for testing
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create default role
    async with async_session() as session:
        default_role = Role(name="user")
        session.add(default_role)
        await session.commit()
    
    yield async_session
    
    # Clean up
    await engine.dispose()


@pytest.fixture
async def test_client(test_db):
    """Create a test client with test database"""
    
    async def override_get_db():
        async with test_db() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()
