"""
Authentication utilities applying SOLID principles
"""
from abc import ABC, abstractmethod
from passlib.context import CryptContext
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Protocol
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config import settings
from ..database import get_db
from ..models.user import User


class PasswordHasher(Protocol):
    def hash_password(self, password: str) -> str: ...
    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...


class TokenManager(Protocol):
    def create_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str: ...
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]: ...


class BcryptPasswordHasher:
    def __init__(self, rounds: int = 12):
        self._context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=rounds
        )
    
    def hash_password(self, password: str) -> str:
        return self._context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._context.verify(plain_password, hashed_password)


class JWTTokenManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self._secret_key = secret_key
        self._algorithm = algorithm
    
    def create_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except ExpiredSignatureError:
            return "expired"
        except JWTError:
            return None


# Dependency instances
password_hasher = BcryptPasswordHasher()
token_manager = JWTTokenManager(settings.SECRET_KEY)

# Backward compatibility functions
def hash_password(password: str) -> str:
    return password_hasher.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return hash_password(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    return token_manager.create_token(data, expires_delta)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    return token_manager.decode_token(token)


class UserAuthenticator:
    def __init__(self, token_manager: TokenManager, security: HTTPBearer):
        self._token_manager = token_manager
        self._security = security
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials,
        db: AsyncSession
    ) -> User:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        payload = self._token_manager.decode_token(credentials.credentials)
        
        if payload == "expired":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("user_id") or payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        result = await db.execute(select(User).filter(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user


security = HTTPBearer(auto_error=False)
user_authenticator = UserAuthenticator(token_manager, security)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    return await user_authenticator.get_current_user(credentials, db)
