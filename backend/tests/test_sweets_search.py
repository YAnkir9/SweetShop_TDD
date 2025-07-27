"""
Tests for the Sweet Shop search endpoint following TDD approach.
Focus: Name search, category filter, price range filter, and no-match handling.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.user import User
from app.models.role import Role
from app.models.sweet import Sweet
from app.models.category import Category
from app.utils.auth import create_access_token, hash_password


@pytest.mark.asyncio
async def test_search_sweets_by_name(async_client: AsyncClient, test_db_session: AsyncSession):
    # Setup: Create user, category and sweets

    # Create customer role
    customer_role = Role(name="customer")
    test_db_session.add(customer_role)
    await test_db_session.flush()
    role_id = customer_role.id

    user = User(username="testuser", email="testuser@example.com", password_hash=hash_password("password"), role_id=role_id, is_verified=True)
    test_db_session.add(user)
    await test_db_session.flush()
    user_id = user.id

    category = Category(name=f"BarfiCategory_{uuid.uuid4().hex[:6]}")
    test_db_session.add(category)
    await test_db_session.flush()

    sweets = [
        Sweet(name="Kaju Barfi", price=120.0, category_id=category.id),
        Sweet(name="Milk Barfi", price=90.0, category_id=category.id),
        Sweet(name="Gulab Jamun", price=100.0, category_id=category.id)
    ]
    test_db_session.add_all(sweets)
    await test_db_session.commit()

    # Token for customer
    token = create_access_token({"sub": str(user_id), "role": "customer"})

    # Search by name
    response = await async_client.get(
        "/api/sweets/search?name=barfi",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("Barfi" in sweet["name"] for sweet in data)


@pytest.mark.asyncio
async def test_search_sweets_by_category(async_client: AsyncClient, test_db_session: AsyncSession):
    # Setup: Create user, categories and sweets

    # Create customer role
    customer_role = Role(name="customer")
    test_db_session.add(customer_role)
    await test_db_session.flush()
    role_id = customer_role.id

    user = User(username="testuser2", email="testuser2@example.com", password_hash=hash_password("password"), role_id=role_id, is_verified=True)
    test_db_session.add(user)
    await test_db_session.flush()
    user_id = user.id

    milk_cat_name = f"milk-based-{uuid.uuid4()}"
    milk_cat = Category(name=milk_cat_name)
    sugar_cat = Category(name=f"sugar-based-{uuid.uuid4()}")
    test_db_session.add_all([milk_cat, sugar_cat])
    await test_db_session.flush()

    sweets = [
        Sweet(name="Milk Peda", price=85.0, category_id=milk_cat.id),
        Sweet(name="Rasgulla", price=95.0, category_id=milk_cat.id),
        Sweet(name="Jalebi", price=60.0, category_id=sugar_cat.id)
    ]
    test_db_session.add_all(sweets)
    await test_db_session.commit()

    token = create_access_token({"sub": str(user_id), "role": "customer"})

    response = await async_client.get(
        f"/api/sweets/search?category={milk_cat_name}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(sweet["category"]["name"] == milk_cat_name for sweet in data)


@pytest.mark.asyncio
async def test_search_sweets_by_price_range(async_client: AsyncClient, test_db_session: AsyncSession):
    # Setup: Create user, one category, multiple price points

    # Create customer role
    customer_role = Role(name="customer")
    test_db_session.add(customer_role)
    await test_db_session.flush()
    role_id = customer_role.id

    user = User(username="testuser3", email="testuser3@example.com", password_hash=hash_password("password"), role_id=role_id, is_verified=True)
    test_db_session.add(user)
    await test_db_session.flush()
    user_id = user.id

    category = Category(name=f"price-test-{uuid.uuid4()}")
    test_db_session.add(category)
    await test_db_session.flush()

    sweets = [
        Sweet(name="Low Price Sweet", price=40.0, category_id=category.id),
        Sweet(name="Mid Price Sweet", price=75.0, category_id=category.id),
        Sweet(name="High Price Sweet", price=120.0, category_id=category.id),
        Sweet(name="Ultra Premium Sweet", price=200.0, category_id=category.id),
    ]
    test_db_session.add_all(sweets)
    await test_db_session.commit()

    token = create_access_token({"sub": str(user_id), "role": "customer"})

    response = await async_client.get(
        "/api/sweets/search?min_price=60&max_price=150",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    prices = [sweet["price"] for sweet in data]
    assert all(60 <= price <= 150 for price in prices)


@pytest.mark.asyncio
async def test_search_returns_empty_when_no_match(async_client: AsyncClient, test_db_session: AsyncSession):
    # Create customer role
    customer_role = Role(name="customer")
    test_db_session.add(customer_role)
    await test_db_session.flush()
    role_id = customer_role.id

    user = User(username="testuser4", email="testuser4@example.com", password_hash=hash_password("password"), role_id=role_id, is_verified=True)

    test_db_session.add(user)
    await test_db_session.flush()
    user_id = user.id
    await test_db_session.commit()  # Ensure user is committed

    token = create_access_token({"sub": str(user_id), "role": "customer"})

    response = await async_client.get(
        "/api/sweets/search?name=nonexistent",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == []
