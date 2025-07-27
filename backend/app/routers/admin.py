"""Admin Router - Admin-only endpoints with role-based authorization"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from app.database import get_db
from app.models.user import User
from app.models.role import Role
from app.models.sweet import Sweet
from app.models.restock import Restock
from app.models.sweet_inventory import SweetInventory
from app.utils.auth import decode_access_token, get_current_user
from app.utils.admin import require_admin_role
from app.utils.sweet_utils import get_sweet_or_404
from app.services.audit_service_simple import AuditService, AuditAction, log_admin_action

router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer(auto_error=False)

# Pydantic models for request/response
class RestockRequest(BaseModel):
    sweet_id: int = Field(..., gt=0, description="ID of the sweet to restock")
    quantity_added: int = Field(..., gt=0, description="Quantity to add to inventory")

class RestockResponse(BaseModel):
    sweet_id: int
    quantity_added: int
    admin_id: int

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: str

class UsersListResponse(BaseModel):
    users: List[UserResponse]
    total_count: int


@router.get("/users", response_model=UsersListResponse)
async def get_all_users(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get all users - Admin only endpoint"""
    
    # Check if credentials are provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify admin access
    current_user = await require_admin_role(credentials.credentials, db)
    
    # Fetch all users with their roles
    stmt = select(User, Role).join(Role, User.role_id == Role.id)
    result = await db.execute(stmt)
    user_role_pairs = result.all()
    
    # Format response
    users = []
    for user, role in user_role_pairs:
        users.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=role.name,
            created_at=user.created_at.isoformat() if user.created_at else ""
        ))
    
    # Log admin action
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        admin_id=current_user.id,
        action=AuditAction.VIEW_USERS,
        details={"users_count": len(users)}
    )
    
    return UsersListResponse(
        users=users,
        total_count=len(users)
    )


@router.post("/restock", response_model=RestockResponse, status_code=status.HTTP_201_CREATED)
async def restock_inventory(
    restock_data: RestockRequest,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Restock inventory - Admin only endpoint"""
    
    # Check if credentials are provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify admin access
    current_user = await require_admin_role(credentials.credentials, db)
    
    # Check if sweet exists
    sweet = await get_sweet_or_404(db, restock_data.sweet_id)
    
    # Update inventory quantity
    inventory_stmt = select(SweetInventory).where(SweetInventory.sweet_id == restock_data.sweet_id)
    inventory_result = await db.execute(inventory_stmt)
    inventory = inventory_result.scalar_one_or_none()
    
    if inventory:
        inventory.quantity += restock_data.quantity_added
    else:
        # Create new inventory record if doesn't exist
        inventory = SweetInventory(
            sweet_id=restock_data.sweet_id,
            quantity=restock_data.quantity_added
        )
        db.add(inventory)
    
    # Create restock record
    restock = Restock(
        admin_id=current_user.id,
        sweet_id=restock_data.sweet_id,
        quantity_added=restock_data.quantity_added
    )
    db.add(restock)
    await db.commit()
    await db.refresh(restock)
    
    # Log admin action
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        admin_id=current_user.id,
        action=AuditAction.RESTOCK_INVENTORY,
        details={
            "sweet_id": restock_data.sweet_id,
            "quantity_added": restock_data.quantity_added,
            "restock_id": restock.id
        }
    )
    
    return RestockResponse(
        sweet_id=restock_data.sweet_id,
        quantity_added=restock_data.quantity_added,
        admin_id=current_user.id
    )
