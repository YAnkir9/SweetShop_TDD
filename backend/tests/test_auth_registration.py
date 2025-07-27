"""
Authentication tests - TDD
"""
import pytest
import uuid
from sqlalchemy import select

from app.models import User


def _generate_unique_user_data(prefix: str = "test") -> dict:
    """Generate unique user data for testing"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"{prefix}user_{unique_id}",
        "email": f"{prefix}_{unique_id}@example.com",
        "password": "securepassword123"
    }


class TestUserRegistration:
    """User registration endpoint tests"""
    
    def test_register_user_success(self, client, test_role):
        """Should create user and return 201 with user data"""
        user_data = _generate_unique_user_data()
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["role_id"] == test_role.id
        assert "password" not in data
        assert "id" in data
    
    def test_register_duplicate_email_fails(self, client, test_role):
        """Should reject duplicate email with 400 error"""
        user_data = _generate_unique_user_data("duplicate")
        
        # First registration should succeed
        response1 = client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        user_data["username"] = f"different_{user_data['username']}"
        response2 = client.post("/api/auth/register", json=user_data)
        
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    def test_register_validation_errors(self, client):
        """Should return 422 for invalid input data"""
        # Invalid email format
        response = client.post("/api/auth/register", json={
            "username": "test",
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Password too short
        response = client.post("/api/auth/register", json={
            "username": "test",
            "email": "test@example.com",
            "password": "short"
        })
        assert response.status_code == 422


class TestUserLogin:
    """User login endpoint tests"""
    
    def test_login_user_success(self, client, test_role):
        """Should return 200 with access token for valid credentials"""
        # Register a user first
        user_data = _generate_unique_user_data("login")
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Login with same credentials
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_invalid_credentials(self, client):
        """Should return 401 for wrong email or password"""
        # Test with nonexistent email
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
        
        # Test with wrong password
        response = client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_login_validation_errors(self, client):
        """Should return 422 for invalid input format"""
        # Invalid email format
        response = client.post("/api/auth/login", json={
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Missing fields
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 422


class TestAuthenticationFlow:
    """End-to-end authentication workflow tests"""
    
    def test_register_then_login_flow(self, client, test_role):
        """Should allow login after successful registration"""
        # Register new user
        user_data = _generate_unique_user_data("flow")
        
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Login with same credentials
        login_response = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"
