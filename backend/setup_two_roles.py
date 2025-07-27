"""
Ensure only 2 roles exist in the database: admin and customer
"""
import asyncio
from app.database import async_session
from app.models.role import Role
from sqlalchemy import select, delete


async def setup_two_roles_only():
    """Ensure exactly 2 roles exist: admin and customer"""
    async with async_session() as session:
        try:
            print("Setting up role table with exactly 2 roles...")
            
            # Delete all existing roles first
            await session.execute(delete(Role))
            await session.commit()
            print("Cleared existing roles")
            
            # Create exactly 2 roles
            admin_role = Role(name="admin")
            customer_role = Role(name="customer")
            
            session.add(admin_role)
            session.add(customer_role)
            await session.commit()
            
            # Refresh to get IDs
            await session.refresh(admin_role)
            await session.refresh(customer_role)
            
            print(f"Created roles:")
            print(f"  - admin (ID: {admin_role.id})")
            print(f"  - customer (ID: {customer_role.id})")
            
            # Verify only 2 roles exist
            result = await session.execute(select(Role))
            all_roles = result.scalars().all()
            
            print(f"\nVerification: Found {len(all_roles)} roles in database")
            for role in all_roles:
                print(f"  - {role.name} (ID: {role.id})")
                
            if len(all_roles) != 2:
                print("ERROR: Expected exactly 2 roles!")
                return False
                
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"Error setting up roles: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(setup_two_roles_only())
    if success:
        print("\n✅ Role table setup complete: exactly 2 roles (admin, customer)")
    else:
        print("\n❌ Role table setup failed")
