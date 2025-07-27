from pydantic import BaseModel
from typing import Optional

class SweetCreate(BaseModel):
    name: str
    price: float
    category_id: int
    image_url: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class SweetResponse(BaseModel):
    id: int
    name: str
    price: float
    category: CategoryResponse

    class Config:
        from_attributes = True