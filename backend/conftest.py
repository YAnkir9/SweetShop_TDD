"""
Pytest async fixtures for Sweet Shop
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator

from app.main import app
from app.models.role import Role
from app.models.user import User
from app.utils.auth import hash_password
from app.database import get_database_url, Base


pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Create a test event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()



def get_test_engine():
    return create_async_engine(
        get_database_url(),
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300
    )

def get_test_session_factory():
    return async_sessionmaker(
        bind=get_test_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )


@pytest.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_test_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()







@pytest.fixture
async def async_client():
    from app.database import get_db

    async def override_get_db():
        session_factory = get_test_session_factory()
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_role():
    session_factory = get_test_session_factory()
    async with session_factory() as session:
        result = await session.execute(select(Role).where(Role.name == "customer"))
        role = result.scalar_one_or_none()
        if not role:
            raise Exception("Customer role not found in database")
        return role



