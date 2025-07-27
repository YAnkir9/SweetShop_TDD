"""
Authentication tests - TDD
"""
import pytest
import uuid
from sqlalchemy import select

from app.models import User


def _generate_unique_user_data(prefix: str = "test") -> dict:
    """Generate unique user data for testing"""
    import time
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())
    return {
        "username": f"{prefix}user_{unique_id}_{timestamp}",
        "email": f"{prefix}_{unique_id}_{timestamp}@sweetshop-test.com",
        "password": "securepassword123"
    }


class TestUserRegistration:
    """User registration endpoint tests"""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, async_client, test_role):
        """Should create user and return 201 with user data"""
        user_data = _generate_unique_user_data()
        response = await async_client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["role_id"] == test_role.id
        assert "password" not in data
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email_fails(self, async_client, test_role):
        """Should reject duplicate email with 400 error"""
        user_data = _generate_unique_user_data("duplicate")
        # First registration should succeed
        response1 = await async_client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        # Second registration with same email should fail
        user_data["username"] = f"different_{user_data['username']}"
        response2 = await async_client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_validation_errors(self, async_client):
        """Should return 422 for invalid input data"""
        # Invalid email format
        response = await async_client.post("/api/auth/register", json={
            "username": "test",
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422
        # Password too short
        response = await async_client.post("/api/auth/register", json={
            "username": "test",
            "email": "test@example.com",
            "password": "short"
        })
        assert response.status_code == 422


class TestUserLogin:
    """User login endpoint tests"""
    
    @pytest.mark.asyncio
    async def test_login_user_success(self, async_client, test_role):
        """Should return 200 with access token for valid credentials"""
        # Register a user first
        user_data = _generate_unique_user_data("login")
        register_response = await async_client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        # Login with same credentials
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = await async_client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client):
        """Should return 401 for wrong email or password"""
        import time
        timestamp = int(time.time())
        # Test with nonexistent email
        response = await async_client.post("/api/auth/login", json={
            "email": f"nonexistent_{timestamp}@sweetshop-test.com",
            "password": "password123"
        })
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
        # Test with wrong password
        response = await async_client.post("/api/auth/login", json={
            "email": f"testuser_{timestamp}@sweetshop-test.com", 
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_validation_errors(self, async_client):
        """Should return 422 for invalid input format"""
        import time
        timestamp = int(time.time())
        # Invalid email format
        response = await async_client.post("/api/auth/login", json={
            "email": f"invalid-email-{timestamp}",
            "password": "password123"
        })
        assert response.status_code == 422
        # Missing fields
        response = await async_client.post("/api/auth/login", json={})
        assert response.status_code == 422
