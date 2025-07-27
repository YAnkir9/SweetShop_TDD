"""
Setup script to ensure the two required roles exist in the database
"""
import asyncio
from app.database import async_session
from app.models.role import Role
from sqlalchemy import select


async def setup_roles():
    """Create the two required roles: admin (ID=1) and customer (ID=2)"""
    async with async_session() as session:
        try:
            # Check if admin role exists
            admin_result = await session.execute(select(Role).where(Role.name == "admin"))
            admin_role = admin_result.scalar_one_or_none()
            
            if not admin_role:
                admin_role = Role(name="admin")
                session.add(admin_role)
                print("Created admin role")
            else:
                print(f"Admin role already exists with ID: {admin_role.id}")
            
            # Check if customer role exists
            customer_result = await session.execute(select(Role).where(Role.name == "customer"))
            customer_role = customer_result.scalar_one_or_none()
            
            if not customer_role:
                customer_role = Role(name="customer")
                session.add(customer_role)
                print("Created customer role")
            else:
                print(f"Customer role already exists with ID: {customer_role.id}")
            
            await session.commit()
            
            # Refresh to get IDs
            if admin_role.id is None:
                await session.refresh(admin_role)
            if customer_role.id is None:
                await session.refresh(customer_role)
                
            print(f"Roles setup complete:")
            print(f"  Admin role ID: {admin_role.id}")
            print(f"  Customer role ID: {customer_role.id}")
            
        except Exception as e:
            await session.rollback()
            print(f"Error setting up roles: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(setup_roles())
