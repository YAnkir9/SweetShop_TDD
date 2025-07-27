"""
Test all SQLAlchemy models and their relationships - focused on important schema tests
"""
import pytest
from decimal import Decimal
from app.models import (
    Role, User, Category, Sweet, SweetInventory, 
    Purchase, Restock, Review, AuditLog, RevokedToken
)


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
