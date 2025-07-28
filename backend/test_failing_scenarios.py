#!/usr/bin/env python3
"""
Test the specific failing scenarios from pytest to understand the difference
"""
import asyncio
import sys
sys.path.append('.')


import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app
from app.database import get_db, async_session



@pytest_asyncio.fixture(autouse=True)
async def override_get_db():
    async def _get_test_db():
        session = async_session()
        try:
            yield session
        finally:
            await session.close()
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_duplicate_registration():
    print("🔍 Testing duplicate registration scenario...")
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"duplicateuser_{unique_id}",
        "email": f"duplicate_{unique_id}@example.com",
        "password": "securepassword123"
    }
    print(f"Testing with email: {user_data['email']}")
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First registration
        print("First registration...")
        response1 = await client.post("/api/auth/register", json=user_data)
        print(f"Response 1 status: {response1.status_code}")
        assert response1.status_code == 201, f"Response 1 content: {response1.text}"
        # Second registration with same email
        print("Second registration with same email...")
        user_data["username"] = f"different_{user_data['username']}"
        response2 = await client.post("/api/auth/register", json=user_data)
        print(f"Response 2 status: {response2.status_code}")
        assert response2.status_code == 400, f"Response 2 content: {response2.text}"
        response_data = response2.json()
        assert "already registered" in response_data["detail"].lower(), f"Wrong error message: {response_data}"
        print("✅ Duplicate registration test PASSED!")



@pytest.mark.asyncio
async def test_invalid_login():
    print("\n🔍 Testing invalid login scenario...")
    async with AsyncClient(app=app, base_url="http://test") as client:
        print("Testing nonexistent email...")
        response = await client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        print(f"Response status: {response.status_code}")
        assert response.status_code == 401, f"Response content: {response.text}"
        response_data = response.json()
        assert "invalid credentials" in response_data["detail"].lower(), f"Wrong error message: {response_data}"
        print("✅ Invalid login test PASSED!")


