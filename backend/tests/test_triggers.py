"""
Test database triggers for automatic timestamps and audit logging
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import User, Role, Sweet, Category, SweetInventory, Purchase, Restock, AuditLog
from app.database import Base, SQLALCHEMY_DATABASE_URL
from app.triggers import create_triggers, drop_triggers
from datetime import datetime
from decimal import Decimal
import asyncio


@pytest.fixture
async def test_engine_with_triggers():
    """Create test engine with triggers"""
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create triggers
    try:
        # Temporarily override the engine in triggers module
        import app.triggers
        original_engine = app.triggers.engine
        app.triggers.engine = engine
        
        await create_triggers()
        
        yield engine
        
        # Cleanup
        await drop_triggers()
        app.triggers.engine = original_engine
        
    finally:
        # Drop all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        await engine.dispose()


@pytest.mark.asyncio
async def test_updated_at_trigger_users(test_engine_with_triggers):
    """Test that updated_at trigger works for users table"""
    engine = test_engine_with_triggers
    
    async with engine.begin() as conn:
        # Insert a role first
        await conn.execute(text("""
            INSERT INTO roles (name) VALUES ('user')
        """))
        
        # Insert a user
        await conn.execute(text("""
            INSERT INTO users (username, email, password_hash, role_id, is_verified, created_at, updated_at)
            VALUES ('testuser', 'test@example.com', 'hash', 1, false, NOW(), NOW())
        """))
        
        # Get initial updated_at
        result = await conn.execute(text("SELECT updated_at FROM users WHERE username = 'testuser'"))
        initial_updated_at = result.scalar()
        
        # Wait a bit to ensure timestamp difference
        await asyncio.sleep(0.1)
        
        # Update the user
        await conn.execute(text("""
            UPDATE users SET email = 'newemail@example.com' WHERE username = 'testuser'
        """))
        
        # Get new updated_at
        result = await conn.execute(text("SELECT updated_at FROM users WHERE username = 'testuser'"))
        new_updated_at = result.scalar()
        
        # Verify updated_at was automatically updated
        assert new_updated_at > initial_updated_at


@pytest.mark.asyncio
async def test_updated_at_trigger_sweets(test_engine_with_triggers):
    """Test that updated_at trigger works for sweets table"""
    engine = test_engine_with_triggers
    
    async with engine.begin() as conn:
        # Insert a category first
        await conn.execute(text("""
            INSERT INTO categories (name) VALUES ('chocolates')
        """))
        
        # Insert a sweet
        await conn.execute(text("""
            INSERT INTO sweets (name, category_id, price, is_deleted, created_at, updated_at)
            VALUES ('Dark Chocolate', 1, 9.99, false, NOW(), NOW())
        """))
        
        # Get initial updated_at
        result = await conn.execute(text("SELECT updated_at FROM sweets WHERE name = 'Dark Chocolate'"))
        initial_updated_at = result.scalar()
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Update the sweet
        await conn.execute(text("""
            UPDATE sweets SET price = 10.99 WHERE name = 'Dark Chocolate'
        """))
        
        # Get new updated_at
        result = await conn.execute(text("SELECT updated_at FROM sweets WHERE name = 'Dark Chocolate'"))
        new_updated_at = result.scalar()
        
        # Verify updated_at was automatically updated
        assert new_updated_at > initial_updated_at


@pytest.mark.asyncio
async def test_purchase_audit_trigger(test_engine_with_triggers):
    """Test that purchase audit trigger creates audit log entries"""
    engine = test_engine_with_triggers
    
    async with engine.begin() as conn:
        # Setup required data
        await conn.execute(text("INSERT INTO roles (name) VALUES ('user')"))
        await conn.execute(text("INSERT INTO categories (name) VALUES ('chocolates')"))
        await conn.execute(text("""
            INSERT INTO users (username, email, password_hash, role_id, is_verified, created_at, updated_at)
            VALUES ('buyer', 'buyer@example.com', 'hash', 1, true, NOW(), NOW())
        """))
        await conn.execute(text("""
            INSERT INTO sweets (name, category_id, price, is_deleted, created_at, updated_at)
            VALUES ('Dark Chocolate', 1, 9.99, false, NOW(), NOW())
        """))
        
        # Check initial audit log count
        result = await conn.execute(text("SELECT COUNT(*) FROM audit_logs"))
        initial_count = result.scalar()
        
        # Insert a purchase (should trigger audit log)
        await conn.execute(text("""
            INSERT INTO purchases (user_id, sweet_id, quantity_purchased, total_price, purchased_at)
            VALUES (1, 1, 2, 19.98, NOW())
        """))
        
        # Check that audit log was created
        result = await conn.execute(text("SELECT COUNT(*) FROM audit_logs"))
        new_count = result.scalar()
        
        assert new_count == initial_count + 1
        
        # Verify audit log details
        result = await conn.execute(text("""
            SELECT user_id, action, target_table, target_id, metadata
            FROM audit_logs 
            WHERE action = 'PURCHASE'
            ORDER BY created_at DESC 
            LIMIT 1
        """))
        audit_record = result.fetchone()
        
        assert audit_record[0] == 1  # user_id
        assert audit_record[1] == 'PURCHASE'  # action
        assert audit_record[2] == 'purchases'  # target_table
        assert audit_record[3] == 1  # target_id (purchase id)
        
        # Check metadata contains purchase details
        metadata = audit_record[4]
        assert metadata['quantity_purchased'] == 2
        assert float(metadata['total_price']) == 19.98


@pytest.mark.asyncio 
async def test_restock_audit_trigger(test_engine_with_triggers):
    """Test that restock audit trigger creates audit log entries"""
    engine = test_engine_with_triggers
    
    async with engine.begin() as conn:
        # Setup required data
        await conn.execute(text("INSERT INTO roles (name) VALUES ('admin')"))
        await conn.execute(text("INSERT INTO categories (name) VALUES ('chocolates')"))
        await conn.execute(text("""
            INSERT INTO users (username, email, password_hash, role_id, is_verified, created_at, updated_at)
            VALUES ('admin', 'admin@example.com', 'hash', 1, true, NOW(), NOW())
        """))
        await conn.execute(text("""
            INSERT INTO sweets (name, category_id, price, is_deleted, created_at, updated_at)
            VALUES ('Dark Chocolate', 1, 9.99, false, NOW(), NOW())
        """))
        
        # Check initial audit log count
        result = await conn.execute(text("SELECT COUNT(*) FROM audit_logs"))
        initial_count = result.scalar()
        
        # Insert a restock (should trigger audit log)
        await conn.execute(text("""
            INSERT INTO restocks (admin_id, sweet_id, quantity_added, restocked_at)
            VALUES (1, 1, 50, NOW())
        """))
        
        # Check that audit log was created
        result = await conn.execute(text("SELECT COUNT(*) FROM audit_logs"))
        new_count = result.scalar()
        
        assert new_count == initial_count + 1
        
        # Verify audit log details
        result = await conn.execute(text("""
            SELECT user_id, action, target_table, target_id, metadata
            FROM audit_logs 
            WHERE action = 'RESTOCK'
            ORDER BY created_at DESC 
            LIMIT 1
        """))
        audit_record = result.fetchone()
        
        assert audit_record[0] == 1  # user_id (admin_id)
        assert audit_record[1] == 'RESTOCK'  # action
        assert audit_record[2] == 'restocks'  # target_table
        assert audit_record[3] == 1  # target_id (restock id)
        
        # Check metadata contains restock details
        metadata = audit_record[4]
        assert metadata['quantity_added'] == 50


@pytest.mark.asyncio
async def test_sweet_inventory_updated_at_trigger(test_engine_with_triggers):
    """Test that updated_at trigger works for sweet_inventory table"""
    engine = test_engine_with_triggers
    
    async with engine.begin() as conn:
        # Setup required data
        await conn.execute(text("INSERT INTO categories (name) VALUES ('chocolates')"))
        await conn.execute(text("""
            INSERT INTO sweets (name, category_id, price, is_deleted, created_at, updated_at)
            VALUES ('Dark Chocolate', 1, 9.99, false, NOW(), NOW())
        """))
        
        # Insert inventory
        await conn.execute(text("""
            INSERT INTO sweet_inventory (sweet_id, quantity, updated_at)
            VALUES (1, 100, NOW())
        """))
        
        # Get initial updated_at
        result = await conn.execute(text("SELECT updated_at FROM sweet_inventory WHERE sweet_id = 1"))
        initial_updated_at = result.scalar()
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Update inventory
        await conn.execute(text("""
            UPDATE sweet_inventory SET quantity = 150 WHERE sweet_id = 1
        """))
        
        # Get new updated_at
        result = await conn.execute(text("SELECT updated_at FROM sweet_inventory WHERE sweet_id = 1"))
        new_updated_at = result.scalar()
        
        # Verify updated_at was automatically updated
        assert new_updated_at > initial_updated_at
