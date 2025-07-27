"""Common utilities for sweet-related operations"""

from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.sweet import Sweet


async def get_sweet_or_404(db: AsyncSession, sweet_id: int, load_relations: bool = False) -> Sweet:
    """
    Get a sweet by ID or raise 404 if not found.
    
    Args:
        db: Database session
        sweet_id: ID of the sweet to retrieve
        load_relations: Whether to load category and reviews relationships
    
    Returns:
        Sweet object if found
        
    Raises:
        HTTPException: 404 if sweet not found or is deleted
    """
    query = select(Sweet).where(Sweet.id == sweet_id, Sweet.is_deleted == False)
    
    if load_relations:
        query = query.options(
            selectinload(Sweet.category),
            selectinload(Sweet.reviews)
        )
    
    result = await db.execute(query)
    sweet = result.scalar_one_or_none()
    
    if not sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    return sweet


def validate_rating(rating: int) -> None:
    """
    Validate that a rating is within the allowed range (1-5).
    
    Args:
        rating: The rating value to validate
        
    Raises:
        HTTPException: 400 if rating is not between 1 and 5
    """
    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
