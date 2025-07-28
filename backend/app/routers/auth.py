"""
Authentication router with clean architecture
"""
from abc import ABC, abstractmethod
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


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_default_role(self) -> Role:
        result = await self.db.execute(select(Role).filter(Role.name == "customer"))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default role not found"
            )
        return role
    
    async def create_user(self, user_data: UserCreate) -> User:
        role = await self.get_default_role()
        hashed_password = hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            role_id=role.id,
            address_line1=user_data.address_line1,
            address_line2=user_data.address_line2,
            city=user_data.city,
            state=user_data.state,
            postal_code=user_data.postal_code,
            country=user_data.country
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        await self._validate_user_uniqueness(user_data.email, user_data.username)
        user = await self.user_repo.create_user(user_data)
        return UserResponse.model_validate(user)
    
    async def login_user(self, login_data: UserLogin) -> Token:
        user = await self.user_repo.get_by_email(login_data.email)
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def _validate_user_uniqueness(self, email: str, username: str) -> None:
        if await self.user_repo.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if await self.user_repo.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )


router = APIRouter(prefix="/api/auth", tags=["authentication"])

# New endpoint to get user by email
@router.get("/users/by-email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    return AuthService(user_repo)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    return await auth_service.login_user(login_data)
