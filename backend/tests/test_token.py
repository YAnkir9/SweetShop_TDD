"""
JWT Token validation tests - TDD
"""
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import status


class TestTokenValidation:
    """JWT token validation tests for protected routes"""
    
    def test_missing_token_returns_401(self, client):
        """Should return 401 when no Authorization header is provided"""
        response = client.get("/api/sweets")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "not authenticated" in response.json()["detail"].lower()
    
    def test_valid_token_allows_access(self, client, valid_token, test_user_for_token):
        """Should return 200 when valid token is provided"""
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/api/sweets", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_expired_token_returns_401(self, client, expired_token):
        """Should return 401 when expired token is provided"""
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/sweets", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "token expired" in response.json()["detail"].lower()
    
    def test_invalid_signature_returns_401(self, client, invalid_signature_token):
        """Should return 401 when token has invalid signature"""
        headers = {"Authorization": f"Bearer {invalid_signature_token}"}
        response = client.get("/api/sweets", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid token" in response.json()["detail"].lower()
    
    def test_token_without_bearer_prefix_returns_401(self, client, valid_token):
        """Should return 401 when token is provided without 'Bearer' prefix"""
        headers = {"Authorization": valid_token}
        response = client.get("/api/sweets", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "not authenticated" in response.json()["detail"].lower()
    
    def test_malformed_token_returns_401(self, client):
        """Should return 401 when token is malformed"""
        headers = {"Authorization": "Bearer invalid.token.format"}
        response = client.get("/api/sweets", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid token" in response.json()["detail"].lower()
    
    def test_empty_bearer_token_returns_401(self, client):
        """Should return 401 when Bearer token is empty"""
        headers = {"Authorization": "Bearer "}
        response = client.get("/api/sweets", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "not authenticated" in response.json()["detail"].lower()


@pytest.fixture
def valid_token(jwt_settings):
    """Generate a valid JWT token for testing"""
    payload = {
        "sub": "test@example.com",
        "user_id": 1,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, jwt_settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def expired_token(jwt_settings):
    """Generate an expired JWT token for testing"""
    payload = {
        "sub": "test@example.com",
        "user_id": 1,
        "exp": datetime.utcnow() - timedelta(hours=1),
        "iat": datetime.utcnow() - timedelta(hours=2)
    }
    return jwt.encode(payload, jwt_settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def invalid_signature_token(jwt_settings):
    """Generate a token with invalid signature for testing"""
    payload = {
        "sub": "test@example.com",
        "user_id": 1,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    # Use wrong secret to create invalid signature
    return jwt.encode(payload, "wrong_secret", algorithm="HS256")


@pytest.fixture
async def test_user_for_token(test_role):
    """Create a test user for token validation"""
    from app.models.user import User
    from app.utils.auth import hash_password
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    
    # Use same database as main for consistency
    TEST_DATABASE_URL = "postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop"
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if user already exists
        from sqlalchemy import select
        result = await session.execute(select(User).filter(User.id == 1))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            await engine.dispose()
            return existing_user
            
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("password123"),
            role_id=test_role.id
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    await engine.dispose()
    return user


@pytest.fixture
def jwt_settings():
    """Get real JWT settings from config for testing"""
    from app.config import settings
    return settings