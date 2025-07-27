from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from decimal import Decimal

from ..database import get_db
from ..utils.auth import get_current_user
from ..models.user import User
from ..models.sweet import Sweet
from ..models.sweet_inventory import SweetInventory
from ..models.purchase import Purchase
from ..schemas.purchase import PurchaseCreate, PurchaseResponse

router = APIRouter(prefix="/api", tags=["purchases"])

@router.post("/purchases", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    purchase_data: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PurchaseResponse:
    """Create a new purchase for authenticated customer"""
    
    # Check if sweet exists and is not deleted
    sweet_result = await db.execute(
        select(Sweet).where(Sweet.id == purchase_data.sweet_id, Sweet.is_deleted == False)
    )
    sweet = sweet_result.scalar_one_or_none()
    if not sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    # Check inventory availability
    inventory_result = await db.execute(
        select(SweetInventory).where(SweetInventory.sweet_id == purchase_data.sweet_id)
    )
    inventory = inventory_result.scalar_one_or_none()
    
    if not inventory or inventory.quantity < purchase_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock available"
        )
    
    # Calculate total price
    total_price = float(sweet.price) * purchase_data.quantity
    
    # Create purchase record
    new_purchase = Purchase(
        user_id=current_user.id,
        sweet_id=purchase_data.sweet_id,
        quantity_purchased=purchase_data.quantity,
        total_price=Decimal(str(total_price))
    )
    
    # Update inventory (deduct purchased quantity)
    inventory.quantity -= purchase_data.quantity
    
    # Save to database
    db.add(new_purchase)
    await db.commit()
    await db.refresh(new_purchase)
    
    return PurchaseResponse.model_validate(new_purchase)

@router.get("/purchases", response_model=List[PurchaseResponse])
async def get_user_purchases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[PurchaseResponse]:
    """Get all purchases for the authenticated user"""
    
    result = await db.execute(
        select(Purchase).where(Purchase.user_id == current_user.id).order_by(Purchase.purchased_at.desc())
    )
    purchases = result.scalars().all()
    
    return [PurchaseResponse.model_validate(purchase) for purchase in purchases]
