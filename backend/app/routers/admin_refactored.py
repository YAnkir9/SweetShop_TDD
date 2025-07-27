"""
Refactored Admin Router - Following SOLID Principles and Clean Architecture
Author: AI Assistant
Created: 2024
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database_manager import get_db_session
from app.services.admin_service import AdminService, AdminServiceFactory
from app.services.audit_service import AuditService
from app.utils.admin import require_admin_role
from app.models.user import User

# Router configuration
router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_role)]
)


# Dependency injection functions
async def get_admin_service(
    db: AsyncSession = Depends(get_db_session)
) -> AdminService:
    """
    Create admin service with all dependencies
    Following Dependency Inversion Principle
    """
    audit_service = AuditService(db)
    return AdminServiceFactory.create(db, audit_service)


@router.get("/users")
async def get_all_users(
    current_user: User = Depends(require_admin_role),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    Get all users - Delegating to service layer
    
    - Single Responsibility: Router only handles HTTP concerns
    - Dependency Inversion: Depends on abstractions, not concretions
    """
    try:
        users = await admin_service.get_all_users(admin_id=current_user.id)
        return {
            "success": True,
            "data": {
                "users": [user.dict() for user in users],
                "total_count": len(users)
            },
            "message": f"Retrieved {len(users)} users successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.post("/restock")
async def restock_inventory(
    restock_data: dict,  # Should be proper Pydantic model in production
    current_user: User = Depends(require_admin_role),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    Restock inventory - Delegating to service layer
    
    - Single Responsibility: Router only handles HTTP concerns
    - Open/Closed: New restock types can be added without changing this endpoint
    """
    try:
        sweet_id = restock_data.get("sweet_id")
        quantity_added = restock_data.get("quantity_added")
        
        if not sweet_id or not quantity_added:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sweet_id and quantity_added are required"
            )
        
        if quantity_added <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="quantity_added must be positive"
            )
        
        restock_info = await admin_service.restock_inventory(
            admin_id=current_user.id,
            sweet_id=sweet_id,
            quantity_added=quantity_added
        )
        
        return {
            "success": True,
            "data": restock_info.dict(),
            "message": f"Successfully restocked {quantity_added} units for sweet {sweet_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restock inventory: {str(e)}"
        )


@router.get("/health")
async def admin_health_check(
    current_user: User = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Admin-specific health check including database connectivity
    """
    try:
        from app.services.database_manager import get_database_manager
        
        db_manager = get_database_manager()
        health_status = await db_manager.health_check()
        
        return {
            "success": True,
            "data": {
                "admin_access": True,
                "admin_id": current_user.id,
                "database": health_status
            },
            "message": "Admin system is healthy"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
