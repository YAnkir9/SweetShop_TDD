"""
Authentication tests - TDD Red Cases
"""
import pytest
from sqlalchemy import select

from app.models import User


class TestUserRegistration:
    """User registration endpoint tests"""
    
    def test_register_user_success(self, client, test_role):
        """Should create user and return 201 with user data"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role_id"] == test_role.id
        assert "password" not in data
        assert "id" in data
    
    def test_register_duplicate_email_fails(self, client, test_role):
        """Should reject duplicate email with 400 error"""
        user_data = {
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "securepassword123"
        }
        
        # First registration
        response1 = client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Attempt duplicate email
        user_data["username"] = "user2"
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
        login_data = {
            "email": "user@example.com",
            "password": "correctpassword123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Should return 401 for wrong email or password"""
        # Nonexistent email
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
        
        # Wrong password
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
        register_data = {
            "username": "flowuser",
            "email": "flow@example.com", 
            "password": "securepassword123"
        }
        
        register_response = client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        # Login with same credentials
        login_response = client.post("/api/auth/login", json={
            "email": "flow@example.com",
            "password": "securepassword123"
        })
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
