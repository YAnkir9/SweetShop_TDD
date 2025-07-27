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
from app.utils.auth import create_access_token


@pytest.mark.asyncio
async def test_search_sweets_by_name(async_client: AsyncClient, test_db_session: AsyncSession):
    # Setup: Create category and sweets
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
    token = create_access_token({"sub": "1", "role": "customer"})

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
    # Setup: Create categories and sweets
    milk_cat = Category(name="milk-based")
    sugar_cat = Category(name="sugar-based")
    test_db_session.add_all([milk_cat, sugar_cat])
    await test_db_session.flush()

    sweets = [
        Sweet(name="Milk Peda", price=85.0, category_id=milk_cat.id),
        Sweet(name="Rasgulla", price=95.0, category_id=milk_cat.id),
        Sweet(name="Jalebi", price=60.0, category_id=sugar_cat.id)
    ]
    test_db_session.add_all(sweets)
    await test_db_session.commit()

    token = create_access_token({"sub": "1", "role": "customer"})

    response = await async_client.get(
        "/api/sweets/search?category=milk-based",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(sweet["category"]["name"] == "milk-based" for sweet in data)


@pytest.mark.asyncio
async def test_search_sweets_by_price_range(async_client: AsyncClient, test_db_session: AsyncSession):
    # Setup: One category, multiple price points
    category = Category(name="price-test")
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

    token = create_access_token({"sub": "1", "role": "customer"})

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
async def test_search_returns_empty_when_no_match(async_client: AsyncClient):
    token = create_access_token({"sub": "1", "role": "customer"})

    response = await async_client.get(
        "/api/sweets/search?name=nonexistent",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == []
