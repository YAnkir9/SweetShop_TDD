from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import Dict, Any, List, Optional

from ..utils.auth import get_current_user
from ..models.user import User
from fastapi import Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from ..models.sweet import Sweet
from ..models.category import Category
from ..schemas.sweet import SweetResponse
from ..database import get_db

router = APIRouter(prefix="/api", tags=["sweets"])

@router.get("/sweets", status_code=status.HTTP_200_OK)
async def get_sweets(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    return {
        "message": "Successfully authenticated",
        "user_id": current_user.id,
        "user_email": current_user.email,
        "sweets": []
    }

@router.get("/sweets/search", response_model=List[SweetResponse], status_code=status.HTTP_200_OK)
async def search_sweets(
    name: Optional[str] = Query(None, description="Partial or full name of the sweet"),
    category: Optional[str] = Query(None, description="Category name to filter by"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[SweetResponse]:
    query = select(Sweet).options(selectinload(Sweet.category)).where(Sweet.is_deleted == False)

    if name:
        query = query.where(Sweet.name.ilike(f"%{name}%"))
    if category:
        # Find category by name
        cat_result = await db.execute(select(Category).where(Category.name == category))
        cat_obj = cat_result.scalar_one_or_none()
        if not cat_obj:
            return []  # No such category, return empty
        query = query.where(Sweet.category_id == cat_obj.id)
    if min_price is not None:
        query = query.where(Sweet.price >= min_price)
    if max_price is not None:
        query = query.where(Sweet.price <= max_price)

    result = await db.execute(query.order_by(Sweet.name))
    sweets = result.scalars().all()
    return [SweetResponse.model_validate(s) for s in sweets]
