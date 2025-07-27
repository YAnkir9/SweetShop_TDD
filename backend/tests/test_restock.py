"""
Test suite for restocking functionality - TDD Red Phase
"""
import pytest
import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.role import Role
from app.models.category import Category
from app.models.sweet import Sweet
from app.models.sweet_inventory import SweetInventory
from app.models.restock import Restock
from app.utils.auth import hash_password, create_access_token


@pytest.mark.asyncio
async def test_restock_increases_quantity(async_client, test_db_session: AsyncSession):
    """Test that restocking increases inventory quantity correctly"""
    # Setup: Create admin user, category, sweet, and initial inventory
    admin_role = await test_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = admin_role.scalar_one()
    
    unique_id = uuid.uuid4().hex[:8]
    admin = User(
        username=f"admin_{unique_id}",
        email=f"admin_{unique_id}@example.com",
        password_hash=hash_password("password"),
        role_id=admin_role.id
    )
    test_db_session.add(admin)
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
    
    # Create initial inventory with 10 items
    inventory = SweetInventory(sweet_id=sweet.id, quantity=10)
    test_db_session.add(inventory)
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    
    # Make restock request
    restock_data = {
        "sweet_id": sweet.id,
        "quantity_added": 25
    }
    
    response = await async_client.post(
        "/api/admin/restock",
        json=restock_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify restock was successful
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["sweet_id"] == sweet.id
    assert response_data["quantity_added"] == 25
    
    # Verify inventory was increased
    await test_db_session.refresh(inventory)
    assert inventory.quantity == 35  # 10 + 25 = 35
    
    # Verify restock record was created
    restock_result = await test_db_session.execute(
        select(Restock).where(Restock.admin_id == admin.id, Restock.sweet_id == sweet.id)
    )
    restock = restock_result.scalar_one()
    assert restock.quantity_added == 25


@pytest.mark.asyncio
async def test_restock_with_invalid_id_fails(async_client, test_db_session: AsyncSession):
    """Test that restocking fails with invalid sweet ID"""
    # Setup: Create admin user
    admin_role = await test_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = admin_role.scalar_one()
    
    unique_id = uuid.uuid4().hex[:8]
    admin = User(
        username=f"admin_{unique_id}",
        email=f"admin_{unique_id}@example.com",
        password_hash=hash_password("password"),
        role_id=admin_role.id
    )
    test_db_session.add(admin)
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    
    # Try to restock non-existent sweet
    restock_data = {
        "sweet_id": 999999,  # Non-existent sweet ID
        "quantity_added": 25
    }
    
    response = await async_client.post(
        "/api/admin/restock",
        json=restock_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify restock failed
    assert response.status_code == 404
    response_data = response.json()
    assert "not found" in response_data["detail"].lower()
    
    # Verify no restock record was created
    restock_result = await test_db_session.execute(
        select(Restock).where(Restock.admin_id == admin.id, Restock.sweet_id == 999999)
    )
    restock = restock_result.scalar_one_or_none()
    assert restock is None
