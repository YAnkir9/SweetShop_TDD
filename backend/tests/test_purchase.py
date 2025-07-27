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
def test_customer_can_purchase_sweet(async_client, test_db_session: AsyncSession):
    # TODO: Implement test to verify stock deduction on purchase
    assert False, "Not implemented yet"

@pytest.mark.asyncio
def test_purchase_fails_if_sweet_out_of_stock(async_client, test_db_session: AsyncSession):
    # TODO: Implement test to prevent buying when quantity = 0
    assert False, "Not implemented yet"

@pytest.mark.asyncio
def test_purchase_requires_valid_sweet_id(async_client, test_db_session: AsyncSession):
    # TODO: Implement test to validate sweet existence on purchase
    assert False, "Not implemented yet"
