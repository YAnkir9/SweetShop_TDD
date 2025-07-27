from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from typing import Optional
from ..database import get_db
from ..models import User, Role
from ..schemas import UserCreate, UserResponse, UserLogin, Token
from ..utils.auth import hash_password, verify_password, create_access_token
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])


async def _get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Helper function to get user by email"""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def _get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Helper function to get user by username"""
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()


async def _get_default_role(db: AsyncSession) -> Role:
    """Helper function to get the default user role"""
    result = await db.execute(select(Role).filter(Role.name == "user"))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default role not found"
        )
    return role


async def _validate_user_uniqueness(db: AsyncSession, email: str, username: str) -> None:
    """Validate that email and username are unique"""
    if await _get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if await _get_user_by_username(db, username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user"""
    # Validate uniqueness
    await _validate_user_uniqueness(db, user_data.email, user_data.username)
    
    # Get default role
    role = await _get_default_role(db)
    
    # Create user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role_id=role.id
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse.model_validate(new_user)


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Login user and return JWT token"""
    # Find and validate user
    user = await _get_user_by_email(db, login_data.email)
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )
