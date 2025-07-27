from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    sweet_id: int
    rating: int  # 1-5 stars
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    sweet_id: int
    user_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
