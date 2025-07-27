import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from decimal import Decimal

from app.models.user import User
from app.models.role import Role
from app.models.sweet import Sweet
from app.models.category import Category
from app.models.sweet_inventory import SweetInventory
from app.models.purchase import Purchase
from app.utils.auth import create_access_token, hash_password


@pytest.mark.asyncio
async def test_customer_can_purchase_sweet(async_client, test_db_session: AsyncSession):
    """Test that a customer can successfully purchase a sweet and inventory is deducted"""
    # Setup: Create customer user, category, sweet, and inventory
    customer_role = await test_db_session.execute(select(Role).where(Role.name == "customer"))
    customer_role = customer_role.scalar_one()
    
    unique_id = uuid.uuid4().hex[:8]
    customer = User(
        username=f"customer_{unique_id}",
        email=f"customer_{unique_id}@example.com",
        password_hash=hash_password("password"),
        role_id=customer_role.id
    )
    test_db_session.add(customer)
    await test_db_session.flush()
    
    category = Category(name=f"TestCategory_{unique_id}")
    test_db_session.add(category)
    await test_db_session.flush()
    
    sweet = Sweet(
        name=f"TestSweet_{unique_id}",
        price=Decimal("10.99"),
        category_id=category.id
    )
    test_db_session.add(sweet)
    await test_db_session.flush()
    
    # Create inventory with initial stock
    inventory = SweetInventory(sweet_id=sweet.id, quantity=5)
    test_db_session.add(inventory)
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(customer.id), "role": "customer"})
    
    # Make purchase request
    purchase_data = {
        "sweet_id": sweet.id,
        "quantity": 2
    }
    
    response = await async_client.post(
        "/api/purchases",
        json=purchase_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify purchase was successful
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["sweet_id"] == sweet.id
    assert response_data["quantity_purchased"] == 2
    assert response_data["total_price"] == 21.98  # 2 * 10.99
    
    # Verify inventory was deducted
    await test_db_session.refresh(inventory)
    assert inventory.quantity == 3  # 5 - 2 = 3
    
    # Verify purchase record was created
    purchase_result = await test_db_session.execute(
        select(Purchase).where(Purchase.user_id == customer.id, Purchase.sweet_id == sweet.id)
    )
    purchase = purchase_result.scalar_one()
    assert purchase.quantity_purchased == 2
    assert purchase.total_price == Decimal("21.98")


@pytest.mark.asyncio
async def test_purchase_fails_if_sweet_out_of_stock(async_client, test_db_session: AsyncSession):
    """Test that purchase fails when sweet is out of stock"""
    # Setup: Create customer user, category, sweet, and empty inventory
    customer_role = await test_db_session.execute(select(Role).where(Role.name == "customer"))
    customer_role = customer_role.scalar_one()
    
    unique_id = uuid.uuid4().hex[:8]
    customer = User(
        username=f"customer_{unique_id}",
        email=f"customer_{unique_id}@example.com",
        password_hash=hash_password("password"),
        role_id=customer_role.id
    )
    test_db_session.add(customer)
    await test_db_session.flush()
    
    category = Category(name=f"TestCategory_{unique_id}")
    test_db_session.add(category)
    await test_db_session.flush()
    
    sweet = Sweet(
        name=f"TestSweet_{unique_id}",
        price=Decimal("10.99"),
        category_id=category.id
    )
    test_db_session.add(sweet)
    await test_db_session.flush()
    
    # Create inventory with zero stock
    inventory = SweetInventory(sweet_id=sweet.id, quantity=0)
    test_db_session.add(inventory)
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(customer.id), "role": "customer"})
    
    # Try to make purchase request
    purchase_data = {
        "sweet_id": sweet.id,
        "quantity": 1
    }
    
    response = await async_client.post(
        "/api/purchases",
        json=purchase_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify purchase failed due to insufficient stock
    assert response.status_code == 400
    response_data = response.json()
    assert "insufficient stock" in response_data["detail"].lower()


@pytest.mark.asyncio
async def test_purchase_requires_valid_sweet_id(async_client, test_db_session: AsyncSession):
    """Test that purchase fails with invalid sweet ID"""
    customer_role = await test_db_session.execute(select(Role).where(Role.name == "customer"))
    customer_role = customer_role.scalar_one()
    
    unique_id = uuid.uuid4().hex[:8]
    customer = User(
        username=f"customer_{unique_id}",
        email=f"customer_{unique_id}@example.com",
        password_hash=hash_password("password"),
        role_id=customer_role.id
    )
    test_db_session.add(customer)
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(customer.id), "role": "customer"})
    
    # Try to purchase non-existent sweet
    purchase_data = {
        "sweet_id": 99999,  # Non-existent ID
        "quantity": 1
    }
    
    response = await async_client.post(
        "/api/purchases",
        json=purchase_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify purchase failed due to invalid sweet ID
    assert response.status_code == 404
    response_data = response.json()
    assert "sweet not found" in response_data["detail"].lower()


@pytest.mark.asyncio
async def test_purchase_requires_authentication(async_client, test_db_session: AsyncSession):
    """Test that purchase endpoint requires authentication"""
    purchase_data = {
        "sweet_id": 1,
        "quantity": 1
    }
    
    # Try to make purchase without token
    response = await async_client.post("/api/purchases", json=purchase_data)
    
    # Verify request was rejected due to missing authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_purchase_validates_quantity(async_client, test_db_session: AsyncSession):
    """Test that purchase validates quantity is positive"""
    customer_role = await test_db_session.execute(select(Role).where(Role.name == "customer"))
    customer_role = customer_role.scalar_one()
    
    unique_id = uuid.uuid4().hex[:8]
    customer = User(
        username=f"customer_{unique_id}",
        email=f"customer_{unique_id}@example.com",
        password_hash=hash_password("password"),
        role_id=customer_role.id
    )
    test_db_session.add(customer)
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(customer.id), "role": "customer"})
    
    # Try to purchase with invalid quantity
    purchase_data = {
        "sweet_id": 1,
        "quantity": 0  # Invalid quantity
    }
    
    response = await async_client.post(
        "/api/purchases",
        json=purchase_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify request was rejected due to invalid quantity
    assert response.status_code == 422  # Validation error
