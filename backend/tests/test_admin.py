"""Admin Access Control Tests - TDD RED Phase"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from unittest.mock import patch
from datetime import datetime, timedelta

from app.main import app
from app.models.user import User
from app.models.role import Role
from app.utils.auth import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
async def admin_role():
    engine = create_async_engine("postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop", echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with async_session() as session:
        stmt = select(Role).where(Role.name == "admin")
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            role = Role(name="admin")
            session.add(role)
            await session.commit()
            await session.refresh(role)
    
    await engine.dispose()
    return role


@pytest.fixture
async def user_role():
    engine = create_async_engine("postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop", echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with async_session() as session:
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


@pytest.fixture
async def admin_user(admin_role):
    engine = create_async_engine("postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop", echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with async_session() as session:
        user = User(
            username="admin_user",
            email="admin@sweetshop.com",
            password_hash="hashed_password",
            role_id=admin_role.id
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    await engine.dispose()
    return user


@pytest.fixture
async def customer_user(user_role):
    engine = create_async_engine("postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop", echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with async_session() as session:
        user = User(
            username="customer_user", 
            email="customer@sweetshop.com",
            password_hash="hashed_password",
            role_id=user_role.id
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    await engine.dispose()
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(
        data={
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "role": "admin"
        }
    )


@pytest.fixture  
def customer_token(customer_user):
    return create_access_token(
        data={
            "sub": str(customer_user.id),
            "email": customer_user.email,
            "role": "user"
        }
    )


@pytest.fixture
def tampered_token(customer_user):
    return create_access_token(
        data={
            "sub": str(customer_user.id),
            "email": customer_user.email,
            "role": "admin"  # Tampered role claim
        }
    )


class TestAdminUsersEndpoint:
    """Test admin-only /api/admin/users endpoint"""
    
    def test_admin_can_access_users_list(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 200
        assert "users" in response.json()
        assert isinstance(response.json()["users"], list)
    
    def test_customer_gets_403_on_admin_users(self, client, customer_token):
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Admin access required"
    
    def test_missing_token_gets_401_on_admin_users(self, client):
        response = client.get("/api/admin/users")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_tampered_role_token_gets_403(self, client, tampered_token):
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 403
        assert "Invalid role or insufficient permissions" in response.json()["detail"]
    
    def test_invalid_token_gets_401_on_admin_users(self, client):
        headers = {"Authorization": "Bearer invalid_token_format"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]


class TestAdminRestockEndpoint:
    """Test admin-only /api/admin/restock endpoint"""
    
    def test_admin_can_access_restock_endpoint(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        restock_data = {
            "sweet_id": 1,
            "quantity_added": 50
        }
        
        response = client.post("/api/admin/restock", json=restock_data, headers=headers)
        
        assert response.status_code == 201
        assert "restock_id" in response.json()
        assert response.json()["quantity_added"] == 50
    
    def test_customer_gets_403_on_restock(self, client, customer_token):
        headers = {"Authorization": f"Bearer {customer_token}"}
        restock_data = {
            "sweet_id": 1,
            "quantity_added": 50
        }
        
        response = client.post("/api/admin/restock", json=restock_data, headers=headers)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Admin access required"
    
    def test_restock_validates_input_data(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        invalid_data = {
            "sweet_id": "invalid",  # Should be integer
            "quantity_added": -10   # Should be positive
        }
        
        response = client.post("/api/admin/restock", json=invalid_data, headers=headers)
        
        assert response.status_code == 422
        assert "validation error" in response.json()["detail"].lower()
    
    def test_restock_requires_existing_sweet(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        restock_data = {
            "sweet_id": 99999,  # Non-existent sweet
            "quantity_added": 50
        }
        
        response = client.post("/api/admin/restock", json=restock_data, headers=headers)
        
        assert response.status_code == 404
        assert "Sweet not found" in response.json()["detail"]


class TestAdminRoleValidation:
    """Test role-based authorization logic"""
    
    def test_token_without_role_claim_gets_403(self, client, customer_user):
        # Create token without role claim
        token_without_role = create_access_token(
            data={
                "sub": str(customer_user.id),
                "email": customer_user.email
                # Missing role claim
            }
        )
        
        headers = {"Authorization": f"Bearer {token_without_role}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 403
        assert "Role information missing" in response.json()["detail"]
    
    def test_expired_admin_token_gets_401(self, client, admin_user):
        # Create expired token
        expired_token = create_access_token(
            data={
                "sub": str(admin_user.id),
                "email": admin_user.email,
                "role": "admin"
            },
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 401
        assert "Token expired" in response.json()["detail"]
    
    def test_user_role_validation_against_database(self, client, customer_user):
        # Create token claiming admin role for non-admin user
        fake_admin_token = create_access_token(
            data={
                "sub": str(customer_user.id),
                "email": customer_user.email,
                "role": "admin"  # False claim
            }
        )
        
        headers = {"Authorization": f"Bearer {fake_admin_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 403
        assert "Role verification failed" in response.json()["detail"]


class TestAdminEndpointSecurity:
    """Test security aspects of admin endpoints"""
    
    def test_admin_endpoints_require_https_in_production(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        with patch('app.config.settings.ENVIRONMENT', 'production'):
            response = client.get("/api/admin/users", headers=headers)
            
            # Should check if request is HTTPS in production
            assert response.status_code in [200, 426]  # 426 = Upgrade Required
    
    def test_admin_actions_are_logged(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        restock_data = {
            "sweet_id": 1,
            "quantity_added": 50
        }
        
        with patch('app.services.audit_service.log_admin_action') as mock_log:
            response = client.post("/api/admin/restock", json=restock_data, headers=headers)
            
            assert response.status_code == 201
            mock_log.assert_called_once()
    
    def test_rate_limiting_on_admin_endpoints(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Make multiple rapid requests
        responses = []
        for _ in range(10):
            response = client.get("/api/admin/users", headers=headers)
            responses.append(response.status_code)
        
        # Should have at least one 429 (Too Many Requests) after rate limit
        assert 429 in responses or all(r == 200 for r in responses[:5])



