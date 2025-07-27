from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.role import Role
from app.models.sweet import Sweet
from app.models.category import Category
from app.models.sweet_inventory import SweetInventory
import asyncio
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def seed():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import delete
        from app.models.purchase import Purchase
        from app.models.review import Review
        from app.models.restock import Restock
        from app.models.audit_log import AuditLog
        from app.models.revoked_token import RevokedToken
        # Clear all tables (order matters due to FKs)
        await session.execute(delete(SweetInventory))
        await session.execute(delete(Purchase))
        await session.execute(delete(Review))
        await session.execute(delete(Restock))
        await session.execute(delete(AuditLog))
        await session.execute(delete(RevokedToken))
        await session.execute(delete(Sweet))
        await session.execute(delete(Category))
        await session.execute(delete(User))
        await session.execute(delete(Role))
        await session.commit()

        # Roles
        admin_role = Role(name="admin")
        customer_role = Role(name="customer")
        session.add_all([admin_role, customer_role])
        await session.commit()
        await session.refresh(admin_role)
        await session.refresh(customer_role)

        # Users
        admin = User(username="admin_gj", email="admin@gujaratsweets.com", password_hash="hash", role_id=admin_role.id)
        users = [
            User(username=f"user{i}_gj", email=f"user{i}@gujaratsweets.com", password_hash="hash", role_id=customer_role.id)
            for i in range(1, 5)
        ]
        session.add(admin)
        session.add_all(users)
        await session.commit()

        # Categories (English)
        cat_traditional = Category(name="Traditional Sweets")
        cat_festival = Category(name="Festival Sweets")
        cat_dryfruit = Category(name="Dry Fruit Sweets")
        cat_farsan = Category(name="Farsan")
        session.add_all([cat_traditional, cat_festival, cat_dryfruit, cat_farsan])
        await session.commit()
        await session.refresh(cat_traditional)
        await session.refresh(cat_festival)
        await session.refresh(cat_dryfruit)
        await session.refresh(cat_farsan)

        # Sweets (English)
        sweets = [
            Sweet(name="Kaju Katli", price=450.0, category_id=cat_dryfruit.id, image_url="sweet_images/kaju_katli.jpg"),
            Sweet(name="Jalebi", price=220.0, category_id=cat_festival.id, image_url="sweet_images/jalebi.jpg"),
            Sweet(name="Mohanthal", price=350.0, category_id=cat_traditional.id, image_url="sweet_images/mohanthal.jpg"),
            Sweet(name="Basundi", price=300.0, category_id=cat_traditional.id, image_url="sweet_images/basundi.jpg"),
            Sweet(name="Peda", price=180.0, category_id=cat_festival.id, image_url="sweet_images/peda.jpg"),
            Sweet(name="Rasgulla", price=250.0, category_id=cat_festival.id, image_url="sweet_images/rasgulla.jpg"),
            Sweet(name="Ghari", price=400.0, category_id=cat_traditional.id, image_url="sweet_images/ghari.jpg"),
            Sweet(name="Shakarpara", price=160.0, category_id=cat_farsan.id, image_url="sweet_images/shakarpara.jpg"),
            Sweet(name="Khaman", price=120.0, category_id=cat_farsan.id, image_url="sweet_images/khaman.jpg"),
            Sweet(name="Surti Undhiyu", price=500.0, category_id=cat_farsan.id, image_url="sweet_images/surti_undhiyu.jpg"),
        ]
        session.add_all(sweets)
        await session.commit()
        # Add inventory for each sweet
        for sweet in sweets:
            inv = SweetInventory(sweet_id=sweet.id, quantity=100)
            session.add(inv)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())
