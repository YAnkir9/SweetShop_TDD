from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RestockCreate(BaseModel):
    sweet_id: int
    quantity_added: int

class RestockResponse(BaseModel):
    id: int
    sweet_id: int
    admin_id: int
    quantity_added: int
    restocked_at: datetime

    class Config:
        from_attributes = True
