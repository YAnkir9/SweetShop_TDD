import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.user import User
from app.models.role import Role
from app.models.sweet import Sweet
from app.models.category import Category
from app.models.review import Review
from app.utils.auth import create_access_token

@pytest.mark.asyncio
async def test_gujarati_review_storage_and_retrieval(async_client, test_db_session: AsyncSession):
    """Test that Gujarati language reviews are properly stored and retrieved"""
    
    # Setup roles
    customer_role = await test_db_session.execute(select(Role).where(Role.name == "customer"))
    customer_role = customer_role.scalar_one_or_none()
    if not customer_role:
        customer_role = Role(name="customer")
        test_db_session.add(customer_role)
        await test_db_session.commit()
        await test_db_session.refresh(customer_role)
    
    # Create category and sweet with Gujarati names
    category = Category(name="ગુજરાતી મિઠાઈ")  # Gujarati Sweets
    test_db_session.add(category)
    await test_db_session.commit()
    await test_db_session.refresh(category)
    
    sweet = Sweet(
        name="કાજુ કતલી", 
        description="શુદ્ધ ઘી અને કાજુથી બનેલી પ્રીમિયમ મિઠાઈ",  # Premium sweet made with pure ghee and cashews
        price=450.00, 
        category_id=category.id
    )
    test_db_session.add(sweet)
    await test_db_session.commit()
    await test_db_session.refresh(sweet)
    
    # Create user with Gujarati name
    user_uuid = uuid.uuid4().hex[:8]
    user = User(
        username=f"પ્રિયા_શાહ_{user_uuid}",  # Priya Shah
        email=f"priya_{user_uuid}@example.com",
        password_hash="hash",
        role_id=customer_role.id
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create review with Gujarati comment
    gujarati_comment = "અમદાવાદ માં એવો સ્વાદિષ્ટ કાજુ કતલી ક્યાંય મળતો નથી! Fresh ane pure ghee નો સ્વાદ આવે છે. મારા બાળકોને ખૂબ ગમ્યું. 🙏"
    # Translation: "You can't find such delicious Kaju Katli anywhere in Ahmedabad! You can taste the fresh and pure ghee. My children loved it very much. 🙏"
    
    review = Review(
        user_id=user.id,
        sweet_id=sweet.id,
        rating=5,
        comment=gujarati_comment
    )
    test_db_session.add(review)
    await test_db_session.commit()
    await test_db_session.refresh(review)
    
    # Verify Gujarati text is stored correctly
    stored_review = await test_db_session.execute(
        select(Review).where(Review.id == review.id)
    )
    stored_review = stored_review.scalar_one()
    
    assert stored_review.comment == gujarati_comment
    assert "અમદાવાદ" in stored_review.comment  # Ahmedabad in Gujarati
    assert "સ્વાદિષ્ટ" in stored_review.comment  # Delicious in Gujarati
    assert "કાજુ કતલી" in stored_review.comment  # Kaju Katli in Gujarati
    
    print(f"✅ Gujarati review stored successfully:")
    print(f"Sweet Name (Gujarati): {sweet.name}")
    print(f"Sweet Description (Gujarati): {sweet.description}")
    print(f"User Name (Gujarati): {user.username}")
    print(f"Review Comment (Gujarati): {stored_review.comment}")

@pytest.mark.asyncio
async def test_mixed_language_content_support(async_client, test_db_session: AsyncSession):
    """Test that mixed English-Gujarati content works properly"""
    
    # Setup
    customer_role = await test_db_session.execute(select(Role).where(Role.name == "customer"))
    customer_role = customer_role.scalar_one()
    
    category = Category(name="Traditional Sweets")
    test_db_session.add(category)
    await test_db_session.commit()
    await test_db_session.refresh(category)
    
    sweet = Sweet(
        name="Gujarati Jalebi",
        description="Traditional જલેબી made with સાકર (sugar) and માવો (khoya)",
        price=240.00,
        category_id=category.id
    )
    test_db_session.add(sweet)
    await test_db_session.commit()
    await test_db_session.refresh(sweet)
    
    user_uuid = uuid.uuid4().hex[:8]
    user = User(
        username=f"mixed_user_{user_uuid}",
        email=f"mixed_{user_uuid}@example.com",
        password_hash="hash",
        role_id=customer_role.id
    )
    test_db_session.add(user)
    await test_db_session.commit()
    
    # Mixed language review (common in urban Gujarat)
    mixed_comment = "Very good quality! સારી quality છે and taste પણ સરસ છે. રોજ આવું quality maintain કરજો. Will order again! 👍"
    
    review = Review(
        user_id=user.id,
        sweet_id=sweet.id,
        rating=4,
        comment=mixed_comment
    )
    test_db_session.add(review)
    await test_db_session.commit()
    
    # Verify mixed content is preserved
    stored_review = await test_db_session.execute(
        select(Review).where(Review.user_id == user.id)
    )
    stored_review = stored_review.scalar_one()
    
    assert "quality" in stored_review.comment  # English
    assert "સારી" in stored_review.comment  # Gujarati for "good"
    assert "સરસ" in stored_review.comment  # Gujarati for "nice"
    assert "કરજો" in stored_review.comment  # Gujarati for "please do"
    
    print(f"✅ Mixed language content stored successfully:")
    print(f"Sweet Description (Mixed): {sweet.description}")
    print(f"Review Comment (Mixed): {stored_review.comment}")
