from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class PurchaseCreate(BaseModel):
    sweet_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")

class PurchaseResponse(BaseModel):
    id: int  
    user_id: int
    sweet_id: int
    quantity_purchased: int
    total_price: float
    purchased_at: datetime

    class Config:
        from_attributes = True
