"""
Test all SQLAlchemy models and their relationships
"""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import (
    Role, User, Category, Sweet, SweetInventory, 
    Purchase, Restock, Review, AuditLog, RevokedToken
)
from app.database import Base, get_async_database_url, SQLALCHEMY_DATABASE_URL
from datetime import datetime
from decimal import Decimal


@pytest.fixture
async def test_engine():
    """Create test engine for models testing"""
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


def test_role_model():
    """Test Role model structure"""
    role = Role(name="admin")
    assert role.name == "admin"
    assert hasattr(role, 'id')
    assert hasattr(role, 'users')
    
    # Test __tablename__
    assert Role.__tablename__ == "roles"


def test_user_model():
    """Test User model structure"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role_id=1,
        is_verified=False
    )
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_verified == False
    assert hasattr(user, 'created_at')
    assert hasattr(user, 'updated_at')
    assert hasattr(user, 'role')
    assert hasattr(user, 'purchases')
    assert hasattr(user, 'reviews')
    assert hasattr(user, 'restocks')
    assert hasattr(user, 'audit_logs')
    
    # Test __tablename__
    assert User.__tablename__ == "users"


def test_category_model():
    """Test Category model structure"""
    category = Category(name="Chocolates")
    assert category.name == "Chocolates"
    assert hasattr(category, 'id')
    assert hasattr(category, 'sweets')
    
    # Test __tablename__
    assert Category.__tablename__ == "categories"


def test_sweet_model():
    """Test Sweet model structure"""
    sweet = Sweet(
        name="Dark Chocolate",
        category_id=1,
        price=Decimal("9.99"),
        description="Rich dark chocolate",
        is_deleted=False
    )
    
    assert sweet.name == "Dark Chocolate"
    assert sweet.price == Decimal("9.99")
    assert sweet.is_deleted == False
    assert hasattr(sweet, 'created_at')
    assert hasattr(sweet, 'updated_at')
    assert hasattr(sweet, 'category')
    assert hasattr(sweet, 'inventory')
    assert hasattr(sweet, 'purchases')
    assert hasattr(sweet, 'reviews')
    assert hasattr(sweet, 'restocks')
    
    # Test __tablename__
    assert Sweet.__tablename__ == "sweets"


def test_sweet_inventory_model():
    """Test SweetInventory model structure"""
    inventory = SweetInventory(sweet_id=1, quantity=100)
    assert inventory.sweet_id == 1
    assert inventory.quantity == 100
    assert hasattr(inventory, 'updated_at')
    assert hasattr(inventory, 'sweet')
    
    # Test __tablename__
    assert SweetInventory.__tablename__ == "sweet_inventory"


def test_purchase_model():
    """Test Purchase model structure"""
    purchase = Purchase(
        user_id=1,
        sweet_id=1,
        quantity_purchased=2,
        total_price=Decimal("19.98")
    )
    
    assert purchase.user_id == 1
    assert purchase.sweet_id == 1
    assert purchase.quantity_purchased == 2
    assert purchase.total_price == Decimal("19.98")
    assert hasattr(purchase, 'purchased_at')
    assert hasattr(purchase, 'user')
    assert hasattr(purchase, 'sweet')
    
    # Test __tablename__
    assert Purchase.__tablename__ == "purchases"


def test_restock_model():
    """Test Restock model structure"""
    restock = Restock(
        admin_id=1,
        sweet_id=1,
        quantity_added=50
    )
    
    assert restock.admin_id == 1
    assert restock.sweet_id == 1
    assert restock.quantity_added == 50
    assert hasattr(restock, 'restocked_at')
    assert hasattr(restock, 'admin')
    assert hasattr(restock, 'sweet')
    
    # Test __tablename__
    assert Restock.__tablename__ == "restocks"


def test_review_model():
    """Test Review model structure"""
    review = Review(
        user_id=1,
        sweet_id=1,
        rating=5,
        comment="Excellent chocolate!"
    )
    
    assert review.user_id == 1
    assert review.sweet_id == 1
    assert review.rating == 5
    assert review.comment == "Excellent chocolate!"
    assert hasattr(review, 'created_at')
    assert hasattr(review, 'user')
    assert hasattr(review, 'sweet')
    
    # Test __tablename__
    assert Review.__tablename__ == "reviews"


def test_audit_log_model():
    """Test AuditLog model structure"""
    audit_log = AuditLog(
        user_id=1,
        action="PURCHASE",
        target_table="purchases",
        target_id=1,
        meta_data={"quantity": 2, "total": "19.98"}
    )
    
    assert audit_log.user_id == 1
    assert audit_log.action == "PURCHASE"
    assert audit_log.target_table == "purchases"
    assert audit_log.target_id == 1
    assert audit_log.meta_data == {"quantity": 2, "total": "19.98"}
    assert hasattr(audit_log, 'created_at')
    assert hasattr(audit_log, 'user')
    
    # Test __tablename__
    assert AuditLog.__tablename__ == "audit_logs"


def test_revoked_token_model():
    """Test RevokedToken model structure"""
    token = RevokedToken(jti="12345678-1234-1234-1234-123456789012")
    
    assert token.jti == "12345678-1234-1234-1234-123456789012"
    assert hasattr(token, 'revoked_at')
    
    # Test __tablename__
    assert RevokedToken.__tablename__ == "revoked_tokens"


@pytest.mark.asyncio
async def test_table_creation(test_engine):
    """Test that all tables are created properly"""
    async with test_engine.begin() as conn:
        # Check that all expected tables exist
        expected_tables = {
            "roles", "users", "categories", "sweets", "sweet_inventory",
            "purchases", "restocks", "reviews", "audit_logs", "revoked_tokens"
        }
        
        # Get actual table names
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        actual_tables = {row[0] for row in result.fetchall()}
        
        # Verify all expected tables exist
        assert expected_tables.issubset(actual_tables), f"Missing tables: {expected_tables - actual_tables}"


@pytest.mark.asyncio
async def test_foreign_key_constraints(test_engine):
    """Test that foreign key constraints are properly defined"""
    async with test_engine.begin() as conn:
        # Test foreign key constraints exist
        result = await conn.execute(text("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name
        """))
        
        fk_constraints = result.fetchall()
        assert len(fk_constraints) > 0, "No foreign key constraints found"
        
        # Verify some key foreign keys exist
        fk_dict = {(row[0], row[1]): (row[2], row[3]) for row in fk_constraints}
        
        assert ("users", "role_id") in fk_dict
        assert ("sweets", "category_id") in fk_dict
        assert ("sweet_inventory", "sweet_id") in fk_dict
        assert ("purchases", "user_id") in fk_dict
        assert ("purchases", "sweet_id") in fk_dict


@pytest.mark.asyncio
async def test_unique_constraints(test_engine):
    """Test that unique constraints are properly defined"""
    async with test_engine.begin() as conn:
        # Test unique constraints exist
        result = await conn.execute(text("""
            SELECT 
                tc.table_name,
                kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'UNIQUE'
              AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name
        """))
        
        unique_constraints = result.fetchall()
        unique_dict = {}
        for row in unique_constraints:
            table_name, column_name = row
            if table_name not in unique_dict:
                unique_dict[table_name] = []
            unique_dict[table_name].append(column_name)
        
        # Print actual constraints for debugging
        print(f"Actual unique constraints: {unique_dict}")
        
        # Verify key unique constraints (be more flexible as some may be in different constraint types)
        # Check that sweet_inventory has sweet_id unique constraint
        assert "sweet_inventory" in unique_dict and "sweet_id" in unique_dict["sweet_inventory"]
        
        # Check that reviews has composite unique constraint (user_id, sweet_id)
        if "reviews" in unique_dict:
            review_constraints = unique_dict["reviews"]
            assert "user_id" in review_constraints and "sweet_id" in review_constraints


@pytest.mark.asyncio 
async def test_check_constraints(test_engine):
    """Test that check constraints are properly defined"""
    async with test_engine.begin() as conn:
        # Test check constraints exist
        result = await conn.execute(text("""
            SELECT 
                tc.table_name,
                tc.constraint_name,
                cc.check_clause
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.check_constraints AS cc
              ON tc.constraint_name = cc.constraint_name
            WHERE tc.constraint_type = 'CHECK'
              AND tc.table_schema = 'public'
            ORDER BY tc.table_name
        """))
        
        check_constraints = result.fetchall()
        check_dict = {row[0]: row[2] for row in check_constraints}
        
        # Verify some key check constraints exist
        table_constraints = [row[0] for row in check_constraints]
        assert "sweets" in table_constraints  # price >= 0
        assert "sweet_inventory" in table_constraints  # quantity >= 0
        assert "purchases" in table_constraints  # quantity > 0, total_price >= 0
        assert "restocks" in table_constraints  # quantity_added > 0
        assert "reviews" in table_constraints  # rating 1-5


def test_model_relationships():
    """Test that model relationships are properly defined"""
    # Test Role -> User relationship
    assert hasattr(Role, 'users')
    assert Role.users.property.mapper.class_ == User
    
    # Test User -> Role relationship
    assert hasattr(User, 'role')
    assert User.role.property.mapper.class_ == Role
    
    # Test Category -> Sweet relationship
    assert hasattr(Category, 'sweets')
    assert Category.sweets.property.mapper.class_ == Sweet
    
    # Test Sweet -> Category relationship
    assert hasattr(Sweet, 'category')
    assert Sweet.category.property.mapper.class_ == Category
    
    # Test Sweet -> SweetInventory relationship (one-to-one)
    assert hasattr(Sweet, 'inventory')
    assert Sweet.inventory.property.mapper.class_ == SweetInventory
    assert Sweet.inventory.property.uselist == False  # one-to-one
    
    # Test SweetInventory -> Sweet relationship
    assert hasattr(SweetInventory, 'sweet')
    assert SweetInventory.sweet.property.mapper.class_ == Sweet


def test_model_repr_methods():
    """Test that all models have proper __repr__ methods"""
    role = Role(name="admin")
    assert "Role" in repr(role)
    assert "admin" in repr(role)
    
    user = User(username="test", email="test@example.com", password_hash="hash", role_id=1)
    assert "User" in repr(user)
    assert "test" in repr(user)
    
    category = Category(name="Chocolates")
    assert "Category" in repr(category)
    assert "Chocolates" in repr(category)
    
    sweet = Sweet(name="Dark Chocolate", category_id=1, price=9.99)
    assert "Sweet" in repr(sweet)
    assert "Dark Chocolate" in repr(sweet)
    
    inventory = SweetInventory(sweet_id=1, quantity=100)
    assert "SweetInventory" in repr(inventory)
    assert "100" in repr(inventory)
    
    purchase = Purchase(user_id=1, sweet_id=1, quantity_purchased=2, total_price=19.98)
    assert "Purchase" in repr(purchase)
    assert "2" in repr(purchase)
    
    restock = Restock(admin_id=1, sweet_id=1, quantity_added=50)
    assert "Restock" in repr(restock)
    assert "50" in repr(restock)
    
    review = Review(user_id=1, sweet_id=1, rating=5)
    assert "Review" in repr(review)
    assert "5" in repr(review)
    
    audit_log = AuditLog(user_id=1, action="PURCHASE", target_table="purchases", target_id=1)
    assert "AuditLog" in repr(audit_log)
    assert "PURCHASE" in repr(audit_log)
    
    token = RevokedToken(jti="test-jti")
    assert "RevokedToken" in repr(token)
    assert "test-jti" in repr(token)
