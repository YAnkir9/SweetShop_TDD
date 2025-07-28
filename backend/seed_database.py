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

async def seed_database():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import delete
        from app.models.purchase import Purchase
        from app.models.review import Review
        from app.models.restock import Restock
        from app.models.audit_log import AuditLog
        from app.models.revoked_token import RevokedToken

        # Clear all tables (order matters due to FKs)
        await clear_tables(session)

        # Seed roles
        admin_role, customer_role = await seed_roles(session)

        # Seed users
        await seed_users(session, admin_role, customer_role)

        # Seed categories
        cat_traditional, cat_festival, cat_dryfruit, cat_farsan = await seed_categories(session)

        # Seed sweets and inventory
        await seed_sweets_and_inventory(session, cat_traditional, cat_festival, cat_dryfruit, cat_farsan)

async def clear_tables(session):
    from sqlalchemy import delete
    from app.models.purchase import Purchase
    from app.models.review import Review
    from app.models.restock import Restock
    from app.models.audit_log import AuditLog
    from app.models.revoked_token import RevokedToken
    from app.models.sweet import Sweet
    from app.models.category import Category
    from app.models.sweet_inventory import SweetInventory
    from app.models.user import User
    from app.models.role import Role
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

async def seed_roles(session):
    admin_role = Role(name="admin")
    customer_role = Role(name="customer")
    session.add_all([admin_role, customer_role])
    await session.commit()
    await session.refresh(admin_role)
    await session.refresh(customer_role)
    return admin_role, customer_role

async def seed_users(session, admin_role, customer_role):
    from app.utils.auth import hash_password
    admin_pw = hash_password("hash123")
    admin_user = User(
        username="admin_gj",
        email="admin@gujaratsweets.com",
        password_hash=admin_pw,
        role_id=admin_role.id,
        is_verified=True,
        address_line1="Admin Street",
        address_line2="Suite 1",
        city="Ahmedabad",
        state="Gujarat",
        postal_code="380001"
    )
    users = [
        User(username=f"user{i}_gj", email=f"user{i}@gujaratsweets.com", password_hash=hash_password("hash123"), role_id=customer_role.id)
        for i in range(1, 5)
    ]
    legal_customer = User(
        username="legal_customer",
        email="legal@gujaratsweets.com",
        password_hash=hash_password("legal123"),
        role_id=customer_role.id,
        is_verified=True,
        address_line1="Legal Street",
        address_line2="Suite 2",
        city="Surat",
        state="Gujarat",
        postal_code="395007"
    )
    session.add_all([admin_user] + users + [legal_customer])
    await session.commit()

async def seed_categories(session):
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
    return cat_traditional, cat_festival, cat_dryfruit, cat_farsan

async def seed_sweets_and_inventory(session, cat_traditional, cat_festival, cat_dryfruit, cat_farsan):
    from app.models.sweet import Sweet
    from app.models.sweet_inventory import SweetInventory
    sweets = [
        Sweet(name="Kaju Katli", price=450.0, category_id=cat_dryfruit.id, image_url="sweet_images/kaju_katli.jpg", is_deleted=False),
        Sweet(name="Jalebi", price=220.0, category_id=cat_festival.id, image_url="sweet_images/jalebi.jpg", is_deleted=False),
        Sweet(name="Mohanthal", price=350.0, category_id=cat_traditional.id, image_url="sweet_images/mohanthal.jpg", is_deleted=False),
        Sweet(name="Basundi", price=300.0, category_id=cat_traditional.id, image_url="sweet_images/basundi.jpg", is_deleted=False),
        Sweet(name="Peda", price=180.0, category_id=cat_festival.id, image_url="sweet_images/peda.jpg", is_deleted=False),
        Sweet(name="Rasgulla", price=250.0, category_id=cat_festival.id, image_url="sweet_images/rasgulla.jpg", is_deleted=False),
        Sweet(name="Ghari", price=400.0, category_id=cat_traditional.id, image_url="sweet_images/ghari.jpg", is_deleted=False),
        Sweet(name="Shakarpara", price=160.0, category_id=cat_farsan.id, image_url="sweet_images/shakarpara.jpg", is_deleted=False),
        Sweet(name="Khaman", price=120.0, category_id=cat_farsan.id, image_url="sweet_images/khaman.jpg", is_deleted=False),
        Sweet(name="Surti Undhiyu", price=500.0, category_id=cat_farsan.id, image_url="sweet_images/surti_undhiyu.jpg", is_deleted=False),
    ]
    session.add_all(sweets)
    await session.commit()
    for idx, sweet in enumerate(sweets):
        # Set quantity 0 for first two sweets (simulate out of stock)
        quantity = 0 if idx < 2 else 100
        inv = SweetInventory(sweet_id=sweet.id, quantity=quantity)
        session.add(inv)
    await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_database())
