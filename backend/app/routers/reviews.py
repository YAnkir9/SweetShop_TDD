"""Reviews Router - Customer review endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List

from app.database import get_db
from app.models.user import User
from app.models.sweet import Sweet
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.utils.auth import get_current_user
from app.utils.sweet_utils import get_sweet_or_404, validate_rating
from app.utils.security import validate_user_input

router = APIRouter(prefix="/api/reviews", tags=["reviews"])
security = HTTPBearer(auto_error=False)


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new review for a sweet"""
    
    # Validate rating
    validate_rating(review_data.rating)
    
    # Check if sweet exists
    sweet = await get_sweet_or_404(db, review_data.sweet_id)
    
    # Check if user has already reviewed this sweet
    existing_review_stmt = select(Review).where(
        and_(
            Review.user_id == current_user.id,
            Review.sweet_id == review_data.sweet_id
        )
    )
    existing_review_result = await db.execute(existing_review_stmt)
    existing_review = existing_review_result.scalar_one_or_none()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this sweet"
        )
    
    # Security validation
    validate_user_input(review_data.comment, "comment")
    
    # Create review
    review = Review(
        user_id=current_user.id,
        sweet_id=review_data.sweet_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        sweet_id=review.sweet_id,
        user_id=review.user_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at
    )


@router.get("/sweet/{sweet_id}", response_model=List[ReviewResponse])
async def get_sweet_reviews(
    sweet_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews for a specific sweet"""
    
    # Check if sweet exists
    sweet = await get_sweet_or_404(db, sweet_id)
    
    # Get reviews
    reviews_stmt = select(Review).where(Review.sweet_id == sweet_id).order_by(Review.created_at.desc())
    reviews_result = await db.execute(reviews_stmt)
    reviews = reviews_result.scalars().all()
    
    return [
        ReviewResponse(
            id=review.id,
            sweet_id=review.sweet_id,
            user_id=review.user_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at
        )
        for review in reviews
    ]
