"""
Admin Service Layer - Following SOLID Principles and Clean Architecture
Single Responsibility: Each class has one clear purpose
Open/Closed: Easy to extend without modifying existing code
Liskov Substitution: Proper interfaces and abstractions
Interface Segregation: Focused interfaces
Dependency Inversion: Depends on abstractions, not concretions
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Protocol
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role
from app.models.sweet import Sweet
from app.models.restock import Restock
from app.models.sweet_inventory import SweetInventory
from app.services.audit_service import IAuditService, AuditAction


class AdminError(Exception):
    """Base exception for admin service errors"""
    pass


class UserNotFoundError(AdminError):
    """Raised when user is not found"""
    pass


class SweetNotFoundError(AdminError):
    """Raised when sweet is not found"""
    pass


class DatabaseConnectionError(AdminError):
    """Raised when database connection fails"""
    pass


@dataclass
class UserInfo:
    """Data Transfer Object for user information"""
    id: int
    username: str
    email: str
    role: str
    created_at: str


@dataclass
class RestockInfo:
    """Data Transfer Object for restock information"""
    restock_id: int
    sweet_id: int
    quantity_added: int
    admin_id: int
    timestamp: datetime


class IUserRepository(Protocol):
    """Interface for user data access - Dependency Inversion Principle"""
    
    async def get_all_users_with_roles(self) -> List[tuple[User, Role]]:
        """Get all users with their roles"""
        ...
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        ...


class ISweetRepository(Protocol):
    """Interface for sweet data access - Dependency Inversion Principle"""
    
    async def get_sweet_by_id(self, sweet_id: int) -> Optional[Sweet]:
        """Get sweet by ID"""
        ...
    
    async def is_sweet_available(self, sweet_id: int) -> bool:
        """Check if sweet exists and is not deleted"""
        ...


class IRestockRepository(Protocol):
    """Interface for restock data access - Dependency Inversion Principle"""
    
    async def create_restock(
        self, 
        admin_id: int, 
        sweet_id: int, 
        quantity_added: int
    ) -> Restock:
        """Create a new restock record"""
        ...


class UserRepository:
    """Concrete implementation of user data access - Single Responsibility"""
    
    def __init__(self, db: AsyncSession):
        self._db = db
        self._logger = logging.getLogger(__name__)
    
    async def get_all_users_with_roles(self) -> List[tuple[User, Role]]:
        """Get all users with their roles"""
        try:
            stmt = select(User, Role).join(Role, User.role_id == Role.id)
            result = await self._db.execute(stmt)
            return result.all()
        except SQLAlchemyError as e:
            self._logger.error(f"Database error fetching users: {str(e)}")
            raise DatabaseConnectionError("Failed to fetch users from database")
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await self._db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self._logger.error(f"Database error fetching user {user_id}: {str(e)}")
            raise DatabaseConnectionError(f"Failed to fetch user {user_id}")


class SweetRepository:
    """Concrete implementation of sweet data access - Single Responsibility"""
    
    def __init__(self, db: AsyncSession):
        self._db = db
        self._logger = logging.getLogger(__name__)
    
    async def get_sweet_by_id(self, sweet_id: int) -> Optional[Sweet]:
        """Get sweet by ID"""
        try:
            stmt = select(Sweet).where(Sweet.id == sweet_id)
            result = await self._db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self._logger.error(f"Database error fetching sweet {sweet_id}: {str(e)}")
            raise DatabaseConnectionError(f"Failed to fetch sweet {sweet_id}")
    
    async def is_sweet_available(self, sweet_id: int) -> bool:
        """Check if sweet exists and is not deleted"""
        try:
            stmt = select(Sweet).where(Sweet.id == sweet_id, Sweet.is_deleted == False)
            result = await self._db.execute(stmt)
            sweet = result.scalar_one_or_none()
            return sweet is not None
        except SQLAlchemyError as e:
            self._logger.error(f"Database error checking sweet {sweet_id}: {str(e)}")
            raise DatabaseConnectionError(f"Failed to check sweet {sweet_id}")


class RestockRepository:
    """Concrete implementation of restock data access - Single Responsibility"""
    
    def __init__(self, db: AsyncSession):
        self._db = db
        self._logger = logging.getLogger(__name__)
    
    async def create_restock(
        self, 
        admin_id: int, 
        sweet_id: int, 
        quantity_added: int
    ) -> Restock:
        """Create a new restock record"""
        try:
            restock = Restock(
                admin_id=admin_id,
                sweet_id=sweet_id,
                quantity_added=quantity_added
            )
            self._db.add(restock)
            await self._db.commit()
            await self._db.refresh(restock)
            return restock
        except SQLAlchemyError as e:
            await self._db.rollback()
            self._logger.error(f"Database error creating restock: {str(e)}")
            raise DatabaseConnectionError("Failed to create restock record")


class AdminService:
    """
    Main admin service class - Single Responsibility Principle
    Orchestrates admin operations using repository pattern
    """
    
    def __init__(
        self,
        user_repo: IUserRepository,
        sweet_repo: ISweetRepository,
        restock_repo: IRestockRepository,
        audit_service: IAuditService
    ):
        self._user_repo = user_repo
        self._sweet_repo = sweet_repo
        self._restock_repo = restock_repo
        self._audit_service = audit_service
        self._logger = logging.getLogger(__name__)
    
    async def get_all_users(self, admin_id: int) -> List[UserInfo]:
        """
        Get all users with their roles
        
        Args:
            admin_id: ID of the admin requesting the data
            
        Returns:
            List of UserInfo objects
            
        Raises:
            DatabaseConnectionError: If database operation fails
        """
        try:
            user_role_pairs = await self._user_repo.get_all_users_with_roles()
            
            users = []
            for user, role in user_role_pairs:
                users.append(UserInfo(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    role=role.name,
                    created_at=user.created_at.isoformat() if user.created_at else ""
                ))
            
            # Log admin action
            await self._audit_service.log_admin_action(
                admin_id=admin_id,
                action=AuditAction.VIEW_USERS,
                details={"users_count": len(users)}
            )
            
            return users
            
        except DatabaseConnectionError:
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error in get_all_users: {str(e)}")
            raise AdminError("Failed to retrieve users")
    
    async def restock_inventory(
        self, 
        admin_id: int, 
        sweet_id: int, 
        quantity_added: int
    ) -> RestockInfo:
        """
        Restock inventory for a sweet
        
        Args:
            admin_id: ID of the admin performing the restock
            sweet_id: ID of the sweet to restock
            quantity_added: Quantity to add to inventory
            
        Returns:
            RestockInfo object with restock details
            
        Raises:
            SweetNotFoundError: If sweet doesn't exist
            DatabaseConnectionError: If database operation fails
        """
        try:
            # Validate sweet exists
            if not await self._sweet_repo.is_sweet_available(sweet_id):
                raise SweetNotFoundError(f"Sweet with ID {sweet_id} not found")
            
            # Create restock record
            restock = await self._restock_repo.create_restock(
                admin_id=admin_id,
                sweet_id=sweet_id,
                quantity_added=quantity_added
            )
            
            # Log admin action
            await self._audit_service.log_admin_action(
                admin_id=admin_id,
                action=AuditAction.RESTOCK_INVENTORY,
                details={
                    "sweet_id": sweet_id,
                    "quantity_added": quantity_added,
                    "restock_id": restock.id
                }
            )
            
            return RestockInfo(
                restock_id=restock.id,
                sweet_id=sweet_id,
                quantity_added=quantity_added,
                admin_id=admin_id,
                timestamp=restock.created_at if hasattr(restock, 'created_at') else datetime.utcnow()
            )
            
        except (SweetNotFoundError, DatabaseConnectionError):
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error in restock_inventory: {str(e)}")
            raise AdminError("Failed to restock inventory")


class AdminServiceFactory:
    """Factory for creating admin service with dependencies - Dependency Injection"""
    
    @staticmethod
    def create(db: AsyncSession, audit_service: IAuditService) -> AdminService:
        """Create admin service with all dependencies"""
        user_repo = UserRepository(db)
        sweet_repo = SweetRepository(db)
        restock_repo = RestockRepository(db)
        
        return AdminService(
            user_repo=user_repo,
            sweet_repo=sweet_repo,
            restock_repo=restock_repo,
            audit_service=audit_service
        )
