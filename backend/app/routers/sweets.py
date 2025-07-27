from fastapi import APIRouter, Depends, status, Query, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
from ..models.review import Review
from ..models.user import User
from ..models.role import Role
from ..utils.sweet_utils import get_sweet_or_404
from ..utils.admin import require_admin_role
from ..schemas.sweet import SweetResponse, SweetUpdate, SweetCreate
from ..database import get_db

router = APIRouter(prefix="/api", tags=["sweets"])
security = HTTPBearer(auto_error=False)

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
    query = select(Sweet).options(
        selectinload(Sweet.category),
        selectinload(Sweet.reviews)
    ).where(Sweet.is_deleted == False)

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


@router.get("/sweets/{sweet_id}", response_model=SweetResponse, status_code=status.HTTP_200_OK)
async def get_sweet_detail(
    sweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SweetResponse:
    """Get detailed information about a specific sweet including reviews"""
    # Get sweet with relationships
    sweet = await get_sweet_or_404(db, sweet_id, load_relations=True)
    
    # Get reviews with usernames
    reviews_query = select(Review, User).join(User).where(Review.sweet_id == sweet_id)
    reviews_result = await db.execute(reviews_query)
    review_user_pairs = reviews_result.all()
    
    # Build reviews with usernames
    reviews = []
    for review, user in review_user_pairs:
        reviews.append({
            "id": review.id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
            "username": user.username
        })
    
    # Build response
    return SweetResponse(
        id=sweet.id,
        name=sweet.name,
        price=sweet.price,
        category=sweet.category,
        reviews=reviews
    )


@router.put("/sweets/{sweet_id}", response_model=SweetResponse, status_code=status.HTTP_200_OK)
async def update_sweet(
    sweet_id: int,
    sweet_update: SweetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SweetResponse:
    """Update a sweet - Admin only"""
    
    # Get user's role to check admin access
    user_role_query = select(Role).where(Role.id == current_user.role_id)
    role_result = await db.execute(user_role_query)
    user_role = role_result.scalar_one_or_none()
    
    if not user_role or user_role.name != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update sweets"
        )
    
    # Get existing sweet
    sweet = await get_sweet_or_404(db, sweet_id, load_relations=True)
    
    # Update fields that were provided
    update_data = sweet_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sweet, field, value)
    
    await db.commit()
    await db.refresh(sweet)
    
    # Get reviews with usernames for response
    reviews_query = select(Review, User).join(User).where(Review.sweet_id == sweet_id)
    reviews_result = await db.execute(reviews_query)
    review_user_pairs = reviews_result.all()
    
    reviews = []
    for review, user in review_user_pairs:
        reviews.append({
            "id": review.id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
            "username": user.username
        })
    
    return SweetResponse(
        id=sweet.id,
        name=sweet.name,
        price=sweet.price,
        category=sweet.category,
        reviews=reviews
    )


@router.delete("/sweets/{sweet_id}", status_code=status.HTTP_200_OK)
async def delete_sweet(
    sweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a sweet - Admin only"""
    
    # Get user's role to check admin access
    user_role_query = select(Role).where(Role.id == current_user.role_id)
    role_result = await db.execute(user_role_query)
    user_role = role_result.scalar_one_or_none()
    
    if not user_role or user_role.name != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete sweets"
        )
    
    # Get existing sweet
    sweet = await get_sweet_or_404(db, sweet_id)
    
    # Soft delete
    sweet.is_deleted = True
    await db.commit()
    
    return {"message": "Sweet deleted successfully"}
