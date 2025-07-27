"""Reviews Router - Customer review endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
import re

from app.database import get_db
from app.models.user import User
from app.models.sweet import Sweet
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.utils.auth import get_current_user

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
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Check if sweet exists
    sweet_stmt = select(Sweet).where(Sweet.id == review_data.sweet_id, Sweet.is_deleted == False)
    sweet_result = await db.execute(sweet_stmt)
    sweet = sweet_result.scalar_one_or_none()
    
    if not sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
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
    
    # Security check: Basic SQL injection prevention  
    # Note: This is more about demonstrating awareness than comprehensive protection
    # Real applications should use parameterized queries (which we already do with SQLAlchemy)
    if review_data.comment:
        # Reject obvious attempts to manipulate queries, but allow normal text
        dangerous_patterns = [
            r"\bUNION\s+SELECT\b",
            r"\bINSERT\s+INTO\b", 
            r"\bUPDATE\s+.*\s+SET\b",
            r"\bDELETE\s+FROM\b",
            r"\bCREATE\s+TABLE\b",
            r"\bALTER\s+TABLE\b",
            r"\bEXEC\b|\bEXECUTE\b"
        ]
        
        comment_upper = review_data.comment.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, comment_upper, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
    
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
    sweet_stmt = select(Sweet).where(Sweet.id == sweet_id, Sweet.is_deleted == False)
    sweet_result = await db.execute(sweet_stmt)
    sweet = sweet_result.scalar_one_or_none()
    
    if not sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
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
