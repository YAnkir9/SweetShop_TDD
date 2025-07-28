"""
Authentication schemas with validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = ''.join(c for c in v if c.isalnum() or c == '_')
        return v.lower()


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role_id: int
    is_verified: bool
    
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
