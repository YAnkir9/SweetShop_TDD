"""
Database triggers for automatic timestamp updates and audit logging
"""
from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import AsyncEngine
from .database import engine


UPDATED_AT_TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

AUDIT_LOG_TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION insert_audit_log()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF TG_TABLE_NAME = 'purchases' THEN
            INSERT INTO audit_logs (user_id, action, target_table, target_id, metadata, created_at)
            VALUES (NEW.user_id, 'PURCHASE', TG_TABLE_NAME, NEW.id, 
                    json_build_object('quantity_purchased', NEW.quantity_purchased, 'total_price', NEW.total_price), 
                    NOW());
        ELSIF TG_TABLE_NAME = 'restocks' THEN
            INSERT INTO audit_logs (user_id, action, target_table, target_id, metadata, created_at)
            VALUES (NEW.admin_id, 'RESTOCK', TG_TABLE_NAME, NEW.id, 
                    json_build_object('quantity_added', NEW.quantity_added), 
                    NOW());
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""

UPDATED_AT_TRIGGERS = [
    "CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
    "CREATE TRIGGER update_sweets_updated_at BEFORE UPDATE ON sweets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
    "CREATE TRIGGER update_sweet_inventory_updated_at BEFORE UPDATE ON sweet_inventory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();"
]

AUDIT_LOG_TRIGGERS = [
    "CREATE TRIGGER purchase_audit_trigger AFTER INSERT ON purchases FOR EACH ROW EXECUTE FUNCTION insert_audit_log();",
    "CREATE TRIGGER restock_audit_trigger AFTER INSERT ON restocks FOR EACH ROW EXECUTE FUNCTION insert_audit_log();"
]


async def create_triggers():
    """Create all database triggers"""
    async with engine.begin() as conn:
        await conn.execute(text(UPDATED_AT_TRIGGER_FUNCTION))
        await conn.execute(text(AUDIT_LOG_TRIGGER_FUNCTION))
        
        for trigger_sql in UPDATED_AT_TRIGGERS:
            try:
                await conn.execute(text(trigger_sql))
            except Exception as e:
                if "already exists" not in str(e):
                    raise
        
        for trigger_sql in AUDIT_LOG_TRIGGERS:
            try:
                await conn.execute(text(trigger_sql))
            except Exception as e:
                if "already exists" not in str(e):
                    raise


async def drop_triggers():
    """Drop all database triggers (for testing)"""
    async with engine.begin() as conn:
        drop_triggers_sql = [
            "DROP TRIGGER IF EXISTS update_users_updated_at ON users;",
            "DROP TRIGGER IF EXISTS update_sweets_updated_at ON sweets;", 
            "DROP TRIGGER IF EXISTS update_sweet_inventory_updated_at ON sweet_inventory;",
            "DROP TRIGGER IF EXISTS purchase_audit_trigger ON purchases;",
            "DROP TRIGGER IF EXISTS restock_audit_trigger ON restocks;"
        ]
        
        for drop_sql in drop_triggers_sql:
            await conn.execute(text(drop_sql))
        
        await conn.execute(text("DROP FUNCTION IF EXISTS update_updated_at_column();"))
        await conn.execute(text("DROP FUNCTION IF EXISTS insert_audit_log();"))


@event.listens_for(engine.sync_engine, "connect")
def set_postgresql_search_path(dbapi_connection, connection_record):
    """Set search path for PostgreSQL"""
    with dbapi_connection.cursor() as cursor:
        cursor.execute("SET search_path TO public")


async def setup_database_with_triggers():
    """Setup database with tables and triggers"""
    from .database import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await create_triggers()
