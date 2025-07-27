"""
Database table creation script
Creates all database tables for the Sweet Shop application
"""
import asyncio
from app.database import engine
from app.models.user import Base
import app.models  # Import all models to register them with Base


async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
