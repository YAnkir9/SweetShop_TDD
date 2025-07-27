"""Create test data for development"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from models.sweet import Sweet
from models.role import Role
from models.user import User

async def create_test_data():
    """Create minimal test data"""
    engine = create_async_engine("postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop", echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if test sweet exists
        stmt = select(Sweet).where(Sweet.id == 1)
        result = await session.execute(stmt)
        sweet = result.scalar_one_or_none()
        
        if not sweet:
            # Create a test sweet
            sweet = Sweet(
                id=1,
                name="Test Chocolate",
                category_id=1,  # Assuming category 1 exists
                price=10.99,
                description="Test chocolate for admin tests"
            )
            session.add(sweet)
            await session.commit()
            print("Created test sweet")
        else:
            print("Test sweet already exists")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_data())
