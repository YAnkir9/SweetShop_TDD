"""
JWT Token validation tests - TDD
"""
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import status



import uuid

@pytest.mark.asyncio
async def test_missing_token_returns_401(async_client):
    response = await async_client.get("/api/sweets")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not authenticated" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_valid_token_allows_access(async_client, valid_token, test_user_for_token):
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = await async_client.get("/api/sweets", headers=headers)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_expired_token_returns_401(async_client, expired_token):
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await async_client.get("/api/sweets", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "token expired" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_invalid_signature_returns_401(async_client, invalid_signature_token):
    headers = {"Authorization": f"Bearer {invalid_signature_token}"}
    response = await async_client.get("/api/sweets", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid token" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_token_without_bearer_prefix_returns_401(async_client, valid_token):
    headers = {"Authorization": valid_token}
    response = await async_client.get("/api/sweets", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not authenticated" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_malformed_token_returns_401(async_client):
    headers = {"Authorization": "Bearer invalid.token.format"}
    response = await async_client.get("/api/sweets", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid token" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_empty_bearer_token_returns_401(async_client):
    headers = {"Authorization": "Bearer "}
    response = await async_client.get("/api/sweets", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not authenticated" in response.json()["detail"].lower()


@pytest.fixture
def valid_token(jwt_settings):
    """Generate a valid JWT token for testing (unique per test)"""
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    payload = {
        "sub": unique_email,
        "user_id": 1,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, jwt_settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def expired_token(jwt_settings):
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    payload = {
        "sub": unique_email,
        "user_id": 1,
        "exp": datetime.utcnow() - timedelta(hours=1),
        "iat": datetime.utcnow() - timedelta(hours=2)
    }
    return jwt.encode(payload, jwt_settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def invalid_signature_token(jwt_settings):
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    payload = {
        "sub": unique_email,
        "user_id": 1,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    # Use wrong secret to create invalid signature
    return jwt.encode(payload, "wrong_secret", algorithm="HS256")
@pytest.fixture
async def test_user_for_token(test_role, test_db_session):
    """Create a test user for token validation using shared async test DB/session."""
    from app.models.user import User
    from app.utils.auth import hash_password
    import uuid
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    import uuid
    unique_username = f"testuser_{uuid.uuid4().hex}"
    user = User(
        username=unique_username,
        email=unique_email,
        password_hash=hash_password("password123"),
        role_id=test_role.id
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user


@pytest.fixture
def jwt_settings():
    """Get real JWT settings from config for testing"""
    from app.config import settings
    return settings