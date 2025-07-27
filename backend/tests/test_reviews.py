"""
Test suite for reviews functionality - TDD Red Phase
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
from app.models.review import Review
from app.utils.auth import hash_password, create_access_token


@pytest.mark.asyncio
async def test_authenticated_user_can_review_sweet(async_client, test_db_session: AsyncSession):
    """Test that authenticated user can submit a review for a sweet"""
    # Setup: Create customer user, category, and sweet
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
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(customer.id), "role": "customer"})
    
    # Submit review
    review_data = {
        "sweet_id": sweet.id,
        "rating": 5,
        "comment": "Absolutely delicious! Best sweet ever!"
    }
    
    response = await async_client.post(
        "/api/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify review was created successfully
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["sweet_id"] == sweet.id
    assert response_data["rating"] == 5
    assert response_data["comment"] == "Absolutely delicious! Best sweet ever!"
    assert response_data["user_id"] == customer.id
    
    # Verify review was saved to database
    review_result = await test_db_session.execute(
        select(Review).where(Review.user_id == customer.id, Review.sweet_id == sweet.id)
    )
    review = review_result.scalar_one()
    assert review.rating == 5
    assert review.comment == "Absolutely delicious! Best sweet ever!"


@pytest.mark.asyncio
async def test_user_cannot_review_same_sweet_twice(async_client, test_db_session: AsyncSession):
    """Test that user cannot review the same sweet twice (enforce uniqueness)"""
    # Setup: Create customer user, category, sweet, and initial review
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
    
    # Create initial review
    existing_review = Review(
        user_id=customer.id,
        sweet_id=sweet.id,
        rating=4,
        comment="Good sweet"
    )
    test_db_session.add(existing_review)
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(customer.id), "role": "customer"})
    
    # Try to submit another review for the same sweet
    review_data = {
        "sweet_id": sweet.id,
        "rating": 5,
        "comment": "Changed my mind, it's excellent!"
    }
    
    response = await async_client.post(
        "/api/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify second review was rejected
    assert response.status_code == 400
    response_data = response.json()
    assert "already reviewed" in response_data["detail"].lower()
    
    # Verify only one review exists
    review_result = await test_db_session.execute(
        select(Review).where(Review.user_id == customer.id, Review.sweet_id == sweet.id)
    )
    reviews = review_result.scalars().all()
    assert len(reviews) == 1
    assert reviews[0].rating == 4  # Original review unchanged


@pytest.mark.asyncio
async def test_reviews_returned_with_sweets(async_client, test_db_session: AsyncSession):
    """Test that reviews are included when fetching sweet details"""
    # Setup: Create customer user, category, sweet, and review
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
    
    # Create review
    review = Review(
        user_id=customer.id,
        sweet_id=sweet.id,
        rating=5,
        comment="Amazing taste!"
    )
    test_db_session.add(review)
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(customer.id), "role": "customer"})
    
    # Fetch sweet details
    response = await async_client.get(
        f"/api/sweets/{sweet.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify sweet details include reviews
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == sweet.id
    assert "reviews" in response_data
    assert len(response_data["reviews"]) == 1
    assert response_data["reviews"][0]["rating"] == 5
    assert response_data["reviews"][0]["comment"] == "Amazing taste!"
    assert response_data["reviews"][0]["username"] == customer.username


@pytest.mark.asyncio
async def test_review_requires_authentication(async_client, test_db_session: AsyncSession):
    """Test that review submission requires authentication"""
    # Setup: Create category and sweet (no auth user)
    unique_id = uuid.uuid4().hex[:8]
    category = Category(name=f"TestCategory_{unique_id}")
    test_db_session.add(category)
    await test_db_session.flush()
    
    sweet = Sweet(
        name=f"TestSweet_{unique_id}",
        price=Decimal("10.99"),
        category_id=category.id
    )
    test_db_session.add(sweet)
    await test_db_session.commit()
    
    # Try to submit review without authentication
    review_data = {
        "sweet_id": sweet.id,
        "rating": 5,
        "comment": "Trying to review without auth"
    }
    
    response = await async_client.post(
        "/api/reviews",
        json=review_data
        # No Authorization header
    )
    
    # Verify request was rejected
    assert response.status_code == 401
    response_data = response.json()
    assert "authenticated" in response_data["detail"].lower() or "authorized" in response_data["detail"].lower()


@pytest.mark.asyncio
async def test_review_rejects_sql_injection_input(async_client, test_db_session: AsyncSession):
    """Test security: review endpoint sanitizes SQL injection attempts"""
    # Setup: Create customer user, category, and sweet
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
    await test_db_session.commit()
    
    # Create auth token
    token = create_access_token({"sub": str(customer.id), "role": "customer"})
    
    # Try SQL injection in comment field
    review_data = {
        "sweet_id": sweet.id,
        "rating": 5,
        "comment": "'; DROP TABLE reviews; --"
    }
    
    response = await async_client.post(
        "/api/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify review was created with sanitized input (should not execute SQL)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["comment"] == "'; DROP TABLE reviews; --"  # Comment stored as-is
    
    # Verify database integrity - reviews table still exists and has the review
    review_result = await test_db_session.execute(
        select(Review).where(Review.user_id == customer.id, Review.sweet_id == sweet.id)
    )
    review = review_result.scalar_one()
    assert review.comment == "'; DROP TABLE reviews; --"
    
    # Verify reviews table still exists by counting all reviews
    all_reviews_result = await test_db_session.execute(select(Review))
    all_reviews = all_reviews_result.scalars().all()
    assert len(all_reviews) >= 1  # At least our review exists
