from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SweetCreate(BaseModel):
    name: str
    price: float
    category_id: int
    image_url: Optional[str] = None
    description: Optional[str] = None

class SweetUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    username: Optional[str] = None

    class Config:
        from_attributes = True

class SweetResponse(BaseModel):
    id: int
    name: str
    price: float
    image_url: Optional[str] = None
    category: CategoryResponse
    reviews: Optional[List[ReviewResponse]] = []

    class Config:
        from_attributes = True