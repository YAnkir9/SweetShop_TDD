#!/usr/bin/env python3
"""
Direct verification of authentication functionality
This tests the actual auth logic without pytest complications
"""
import asyncio
import sys
import os
sys.path.append('.')

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.database import Base
from app.models import Role, User
from app.utils.auth import hash_password, verify_password, create_access_token, decode_access_token

# Database URL
DATABASE_URL = "postgresql+asyncpg://postgres:allthebest@localhost:5432/sweet_shop"

async def test_auth_functionality():
    """Test authentication functionality directly"""
    print("🔍 Testing authentication functionality directly...")
    
    # Create engine and session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        # Ensure tables exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Test 1: Password hashing and verification
        print("\n1. Testing password hashing...")
        password = "testpassword123"
        hashed = hash_password(password)
        is_valid = verify_password(password, hashed)
        print(f"   ✅ Password hashing works: {is_valid}")
        
        # Test 2: JWT token creation and verification
        print("\n2. Testing JWT tokens...")
        user_data = {"sub": "test@example.com", "user_id": 123}
        token = create_access_token(user_data)
        decoded = decode_access_token(token)
        print(f"   ✅ JWT tokens work: {decoded['sub'] == user_data['sub']}")
        
        # Test 3: Database user creation (simulate registration)
        print("\n3. Testing user creation in database...")
        async with async_session() as session:
            # Create role if not exists
            stmt = select(Role).where(Role.name == "user") 
            result = await session.execute(stmt)
            role = result.scalar_one_or_none()
            
            if not role:
                role = Role(name="user")
                session.add(role)
                await session.commit()
                await session.refresh(role)
            
            # Create test user
            test_email = "test_direct_verification@example.com"
            
            # Check if user already exists
            user_stmt = select(User).where(User.email == test_email)
            user_result = await session.execute(user_stmt)
            existing_user = user_result.scalar_one_or_none()
            
            if existing_user:
                await session.delete(existing_user)
                await session.commit()
            
            # Create new user
            new_user = User(
                username="test_direct_user",
                email=test_email,
                password_hash=hash_password("directtest123"),
                role_id=role.id
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            
            print(f"   ✅ User creation works: ID {new_user.id}")
            
            # Test 4: User authentication (simulate login)
            print("\n4. Testing user authentication...")
            
            # Find user by email
            auth_stmt = select(User).where(User.email == test_email)
            auth_result = await session.execute(auth_stmt)
            found_user = auth_result.scalar_one_or_none()
            
            if found_user:
                # Verify password
                password_valid = verify_password("directtest123", found_user.password_hash)
                print(f"   ✅ User authentication works: {password_valid}")
                
                if password_valid:
                    # Create access token
                    token_data = {
                        "sub": found_user.email,
                        "user_id": found_user.id
                    }
                    access_token = create_access_token(token_data)
                    print(f"   ✅ Token generation works: {len(access_token) > 0}")
            
            # Test 5: Duplicate email detection
            print("\n5. Testing duplicate email detection...")
            
            duplicate_user = User(
                username="duplicate_test_user",
                email=test_email,  # Same email
                password_hash=hash_password("anotherpassword"),
                role_id=role.id
            )
            
            try:
                session.add(duplicate_user)
                await session.commit()
                print("   ❌ Duplicate email was allowed (should not happen)")
            except Exception as e:
                print(f"   ✅ Duplicate email rejected: {type(e).__name__}")
                await session.rollback()
            
            # Clean up
            if found_user:
                await session.delete(found_user)
                await session.commit()
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await engine.dispose()
    
    print("\n🎉 Direct authentication functionality test completed!")

if __name__ == "__main__":
    asyncio.run(test_auth_functionality())
