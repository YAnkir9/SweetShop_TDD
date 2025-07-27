from pydantic import BaseModel
from typing import Optional

class SweetCreate(BaseModel):
    name: str
    price: float
    category_id: int
    image_url: Optional[str] = None
    description: Optional[str] = None

class SweetResponse(BaseModel):
    id: int
    name: str
    price: float
    category_id: int
    image_url: Optional[str] = None
    description: Optional[str] = None
    is_deleted: bool

    class Config:
        orm_mode = True
