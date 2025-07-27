import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.role import Role
from app.models.sweet import Sweet
from app.utils.auth import create_access_token

@pytest.mark.asyncio
async def test_admin_can_create_sweet(async_client, test_role, test_db_session: AsyncSession):
    admin_user = User(username="adminuser", password_hash="hash", role_id=test_role.id)
    test_db_session.add(admin_user)
    await test_db_session.commit()
    token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
    response = await async_client.post(
        "/api/v1/sweets/",
        json={"name": "Ladoo", "price": 10.0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Ladoo"

@pytest.mark.asyncio
async def test_customer_cannot_create_sweet(async_client, test_role, test_db_session: AsyncSession):
    customer_user = User(username="custuser", password_hash="hash", role_id=test_role.id)
    test_db_session.add(customer_user)
    await test_db_session.commit()
    token = create_access_token({"sub": str(customer_user.id), "role": "customer"})
    response = await async_client.post(
        "/api/v1/sweets/",
        json={"name": "Barfi", "price": 12.0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_all_sweets_returns_list(async_client, test_db_session: AsyncSession):
    response = await async_client.get("/api/v1/sweets/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_sweet_by_admin(async_client, test_role, test_db_session: AsyncSession):
    admin_user = User(username="admin2", password_hash="hash", role_id=test_role.id)
    sweet = Sweet(name="Jalebi", price=15.0)
    test_db_session.add_all([admin_user, sweet])
    await test_db_session.commit()
    token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
    response = await async_client.put(
        f"/api/v1/sweets/{sweet.id}",
        json={"name": "Jalebi Updated", "price": 18.0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Jalebi Updated"

@pytest.mark.asyncio
async def test_delete_sweet_soft_deletes(async_client, test_role, test_db_session: AsyncSession):
    admin_user = User(username="admin3", password_hash="hash", role_id=test_role.id)
    sweet = Sweet(name="Rasgulla", price=20.0)
    test_db_session.add_all([admin_user, sweet])
    await test_db_session.commit()
    token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
    response = await async_client.delete(
        f"/api/v1/sweets/{sweet.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    # Optionally, check DB for soft-delete flag

@pytest.mark.asyncio
async def test_customer_cannot_delete_sweet(async_client, test_role, test_db_session: AsyncSession):
    customer_user = User(username="cust2", password_hash="hash", role_id=test_role.id)
    sweet = Sweet(name="Peda", price=8.0)
    test_db_session.add_all([customer_user, sweet])
    await test_db_session.commit()
    token = create_access_token({"sub": str(customer_user.id), "role": "customer"})
    response = await async_client.delete(
        f"/api/v1/sweets/{sweet.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
