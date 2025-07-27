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
    
    def test_valid_token_allows_access(self, client, valid_token):
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
        assert "invalid authentication" in response.json()["detail"].lower()
    
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
    return jwt.encode(payload, jwt_settings.JWT_SECRET, algorithm=jwt_settings.JWT_ALGORITHM)


@pytest.fixture
def expired_token(jwt_settings):
    """Generate an expired JWT token for testing"""
    payload = {
        "sub": "test@example.com",
        "user_id": 1,
        "exp": datetime.utcnow() - timedelta(hours=1),
        "iat": datetime.utcnow() - timedelta(hours=2)
    }
    return jwt.encode(payload, jwt_settings.JWT_SECRET, algorithm=jwt_settings.JWT_ALGORITHM)


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
    return jwt.encode(payload, "wrong_secret", algorithm=jwt_settings.JWT_ALGORITHM)


@pytest.fixture
def jwt_settings():
    """Mock JWT settings for testing"""
    class JWTSettings:
        JWT_SECRET = "test_secret_key_for_testing"
        JWT_ALGORITHM = "HS256"
    
    return JWTSettings()