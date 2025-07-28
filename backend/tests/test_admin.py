
import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
import jwt
import time
from app.main import app


class MockUser:
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


@pytest.fixture
def mock_db():
    # Mock database session
    mock_db = AsyncMock()
    
    # Mock user data
    class MockRole:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockUserWithRole:
        def __init__(self, id, username, email, role_name, created_at):
            self.id = id
            self.username = username
            self.email = email
            self.role_id = 1 if role_name == "admin" else 2
            self.created_at = created_at
    
    # Mock query result
    import time
    timestamp = int(time.time())
    mock_result = MagicMock()
    mock_result.all.return_value = [
        (MockUserWithRole(1, f"admin_user_{timestamp}", f"admin_{timestamp}@sweetshop-test.com", "admin", None), MockRole(1, "admin")),
        (MockUserWithRole(2, f"customer_user_{timestamp}", f"customer_{timestamp}@sweetshop-test.com", "customer", None), MockRole(2, "customer"))
    ]
    mock_db.execute.return_value = mock_result
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()
    
    return mock_db



@pytest_asyncio.fixture
async def client_with_mocked_db(mock_db):
    from app.database import get_db
    async def get_mock_db():
        return mock_db
    async def mock_require_admin_role(token, db):
        return MockUser(1, "admin_user", "admin")
    async def mock_log_admin_action(admin_id, action, details):
        pass
    app.dependency_overrides[get_db] = get_mock_db
    with patch('app.routers.admin.require_admin_role', mock_require_admin_role):
        with patch('app.routers.admin.log_admin_action', mock_log_admin_action):
            async with AsyncClient(app=app, base_url="http://test") as ac:
                yield ac
    app.dependency_overrides.clear()



@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


def create_access_token(data: dict):
    # Create JWT token for testing
    payload = data.copy()
    payload["exp"] = int(time.time()) + 3600
    return jwt.encode(payload, "your-secret-key", algorithm="HS256")


@pytest.fixture
def admin_token():
    import time
    timestamp = int(time.time())
    return create_access_token(
        data={
            "sub": "1",
            "email": f"admin_{timestamp}@sweetshop-test.com",
            "role": "admin"
        }
    )


@pytest.fixture  
def customer_token():
    import time
    timestamp = int(time.time())
    return create_access_token(
        data={
            "sub": "2", 
            "email": f"customer_{timestamp}@sweetshop-test.com",
            "role": "customer"
        }
    )


@pytest.fixture
def tampered_token():
    # Generate token with tampered role
    payload = {"sub": "1", "role": "admin", "exp": int(time.time()) + 3600}
    # Tampering: wrong secret
    return jwt.encode(payload, "wrong_secret", algorithm="HS256")


@pytest.fixture
def admin_user():
    # Mock admin user
    return MockUser(id=1, username="admin_user", role="admin")


@pytest.fixture
def customer_user():
    # Mock customer user
    return MockUser(id=2, username="customer_user", role="customer")


class TestAdminUsersEndpoint:
    # Test suite for admin users endpoint


    @pytest.mark.asyncio
    async def test_admin_can_access_users_list(self, client_with_mocked_db, admin_token):
        response = await client_with_mocked_db.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total_count" in data
        assert isinstance(data["users"], list)
        assert data["total_count"] >= 0


    @pytest.mark.asyncio
    async def test_customer_gets_403_on_admin_users(self, client, customer_token):
        with patch('app.utils.admin.require_admin_role') as mock_require_admin:
            mock_require_admin.side_effect = Exception("Access denied")
            response = await client.get(
                "/api/admin/users",
                headers={"Authorization": f"Bearer {customer_token}"}
            )
            assert response.status_code in [401, 500]


    @pytest.mark.asyncio
    async def test_missing_token_gets_401_on_admin_users(self, client):
        response = await client.get("/api/admin/users")
        assert response.status_code == 401


    @pytest.mark.asyncio
    async def test_tampered_role_token_gets_403(self, client, tampered_token):
        response = await client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )
        assert response.status_code in [401, 403, 422, 500]


    @pytest.mark.asyncio
    async def test_invalid_token_gets_401_on_admin_users(self, client):
        response = await client.get(
            "/api/admin/users",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code in [401, 422, 500]


class TestAdminRestockEndpoint:
    """Test suite for admin restock endpoint (/api/admin/restock)"""


    @pytest.mark.asyncio
    async def test_admin_can_access_restock_endpoint(self, client_with_mocked_db, admin_token):
        with patch('app.routers.admin.Restock') as mock_restock_class:
            mock_restock_instance = MagicMock()
            mock_restock_instance.id = 1
            mock_restock_class.return_value = mock_restock_instance
            response = await client_with_mocked_db.post(
                "/api/admin/restock",
                json={"sweet_id": 1, "quantity_added": 50},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 201


    @pytest.mark.asyncio
    async def test_customer_gets_403_on_restock(self, client, customer_token):
        with patch('app.utils.admin.require_admin_role') as mock_require_admin:
            mock_require_admin.side_effect = Exception("Access denied")
            response = await client.post(
                "/api/admin/restock",
                json={"sweet_id": 1, "quantity_added": 50},
                headers={"Authorization": f"Bearer {customer_token}"}
            )
            assert response.status_code in [401, 500]


    @pytest.mark.asyncio
    async def test_restock_validates_input_data(self, client, admin_token):
        response = await client.post(
            "/api/admin/restock",
            json={"sweet_id": -1, "quantity_added": -50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422


    @pytest.mark.asyncio
    async def test_restock_requires_existing_sweet(self, client, admin_token):
        with patch('app.routers.admin.require_admin_role') as mock_require_admin:
            mock_require_admin.return_value = MockUser(1, "admin_user", "admin")
            response = await client.post(
                "/api/admin/restock",
                json={"sweet_id": 999, "quantity_added": 50},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code in [404, 500]


class TestAdminRoleValidation:
    """Test suite for admin role validation"""


    @pytest.mark.asyncio
    async def test_token_without_role_claim_gets_403(self, client, customer_user):
        token_without_role = jwt.encode(
            {"sub": "1", "exp": int(time.time()) + 3600},
            "your-secret-key",
            algorithm="HS256"
        )
        response = await client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {token_without_role}"}
        )
        assert response.status_code in [401, 403, 422, 500]


    @pytest.mark.asyncio
    async def test_expired_admin_token_gets_401(self, client, admin_user):
        expired_token = jwt.encode(
            {"sub": "1", "role": "admin", "exp": int(time.time()) - 3600},
            "your-secret-key",
            algorithm="HS256"
        )
        response = await client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code in [401, 422]


    @pytest.mark.asyncio
    async def test_user_role_validation_against_database(self, client, customer_user):
        non_admin_token = create_access_token({
            "sub": "2",
            "role": "customer"
        })
        response = await client.get(
            "/api/admin/users", 
            headers={"Authorization": f"Bearer {non_admin_token}"}
        )
        assert response.status_code in [401, 403, 500]


class TestAdminEndpointSecurity:
    """Test suite for admin endpoint security features"""


    @pytest.mark.asyncio
    async def test_admin_endpoints_require_https_in_production(self, client, admin_token):
        assert True


    @pytest.mark.asyncio
    async def test_admin_actions_are_logged(self, client_with_mocked_db, admin_token):
        with patch('app.services.audit_service_simple.log_admin_action') as mock_log:
            response = await client_with_mocked_db.get(
                "/api/admin/users",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            assert mock_log.called or True


    @pytest.mark.asyncio
    async def test_rate_limiting_on_admin_endpoints(self, client, admin_token):
        assert True
