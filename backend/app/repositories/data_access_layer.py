"""
Data Access Layer (DAL) - Repository Pattern Implementation
Following SOLID Principles and Clean Architecture
Author: AI Assistant
Created: 2024
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.user import User
from app.models.role import Role
from app.models.sweet import Sweet
from app.models.sweet_inventory import SweetInventory
from app.models.restock import Restock
from app.models.audit_log import AuditLog


class DatabaseError(Exception):
    """Base exception for database operations"""
    pass


class EntityNotFoundError(DatabaseError):
    """Exception raised when entity is not found"""
    pass


class IntegrityConstraintError(DatabaseError):
    """Exception raised for integrity constraint violations"""
    pass


# Abstract Repository Interfaces (Dependency Inversion Principle)

class IUserRepository(ABC):
    """Abstract interface for user data access"""
    
    @abstractmethod
    async def get_all_with_roles(self) -> List[Tuple[User, Role]]:
        """Get all users with their roles"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass
    
    @abstractmethod
    async def create(self, user_data: Dict[str, Any]) -> User:
        """Create new user"""
        pass
    
    @abstractmethod
    async def update(self, user_id: int, user_data: Dict[str, Any]) -> User:
        """Update user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Soft delete user"""
        pass


class ISweetRepository(ABC):
    """Abstract interface for sweet data access"""
    
    @abstractmethod
    async def get_all_with_inventory(self) -> List[Tuple[Sweet, Optional[SweetInventory]]]:
        """Get all sweets with inventory information"""
        pass
    
    @abstractmethod
    async def get_by_id(self, sweet_id: int) -> Optional[Sweet]:
        """Get sweet by ID"""
        pass
    
    @abstractmethod
    async def is_available(self, sweet_id: int) -> bool:
        """Check if sweet exists and is not deleted"""
        pass
    
    @abstractmethod
    async def get_inventory(self, sweet_id: int) -> Optional[SweetInventory]:
        """Get inventory for sweet"""
        pass
    
    @abstractmethod
    async def update_inventory(self, sweet_id: int, quantity_change: int) -> SweetInventory:
        """Update inventory quantity"""
        pass


class IRestockRepository(ABC):
    """Abstract interface for restock data access"""
    
    @abstractmethod
    async def create(self, admin_id: int, sweet_id: int, quantity_added: int) -> Restock:
        """Create restock record"""
        pass
    
    @abstractmethod
    async def get_by_sweet_id(self, sweet_id: int, limit: Optional[int] = None) -> List[Restock]:
        """Get restock history for sweet"""
        pass
    
    @abstractmethod
    async def get_by_admin_id(self, admin_id: int, limit: Optional[int] = None) -> List[Restock]:
        """Get restock history by admin"""
        pass


# Concrete Repository Implementations

class UserRepository(IUserRepository):
    """Concrete implementation of user repository"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    async def get_all_with_roles(self) -> List[Tuple[User, Role]]:
        """Get all users with their roles"""
        try:
            result = await self.db_session.execute(
                select(User, Role)
                .join(Role, User.role_id == Role.id)
                .where(User.is_deleted == False)
                .order_by(User.created_at.desc())
            )
            return result.all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching users with roles: {e}")
            raise DatabaseError(f"Failed to fetch users: {str(e)}")
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with role information"""
        try:
            result = await self.db_session.execute(
                select(User)
                .options(selectinload(User.role))
                .where(User.id == user_id, User.is_deleted == False)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching user {user_id}: {e}")
            raise DatabaseError(f"Failed to fetch user: {str(e)}")
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            result = await self.db_session.execute(
                select(User)
                .options(selectinload(User.role))
                .where(User.username == username, User.is_deleted == False)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching user by username {username}: {e}")
            raise DatabaseError(f"Failed to fetch user: {str(e)}")
    
    async def create(self, user_data: Dict[str, Any]) -> User:
        """Create new user"""
        try:
            user = User(**user_data)
            self.db_session.add(user)
            await self.db_session.flush()
            await self.db_session.refresh(user)
            return user
        except IntegrityError as e:
            await self.db_session.rollback()
            self.logger.error(f"Integrity error creating user: {e}")
            raise IntegrityConstraintError(f"User creation failed: {str(e)}")
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            self.logger.error(f"Error creating user: {e}")
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    async def update(self, user_id: int, user_data: Dict[str, Any]) -> User:
        """Update user"""
        try:
            user_data['updated_at'] = datetime.utcnow()
            
            result = await self.db_session.execute(
                update(User)
                .where(User.id == user_id, User.is_deleted == False)
                .values(**user_data)
                .returning(User)
            )
            
            updated_user = result.scalar_one_or_none()
            if not updated_user:
                raise EntityNotFoundError(f"User {user_id} not found")
            
            await self.db_session.flush()
            return updated_user
            
        except EntityNotFoundError:
            raise
        except IntegrityError as e:
            await self.db_session.rollback()
            self.logger.error(f"Integrity error updating user {user_id}: {e}")
            raise IntegrityConstraintError(f"User update failed: {str(e)}")
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            self.logger.error(f"Error updating user {user_id}: {e}")
            raise DatabaseError(f"Failed to update user: {str(e)}")
    
    async def delete(self, user_id: int) -> bool:
        """Soft delete user"""
        try:
            result = await self.db_session.execute(
                update(User)
                .where(User.id == user_id, User.is_deleted == False)
                .values(is_deleted=True, updated_at=datetime.utcnow())
            )
            
            if result.rowcount == 0:
                raise EntityNotFoundError(f"User {user_id} not found")
            
            await self.db_session.flush()
            return True
            
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            self.logger.error(f"Error deleting user {user_id}: {e}")
            raise DatabaseError(f"Failed to delete user: {str(e)}")


class SweetRepository(ISweetRepository):
    """Concrete implementation of sweet repository"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    async def get_all_with_inventory(self) -> List[Tuple[Sweet, Optional[SweetInventory]]]:
        """Get all sweets with inventory information"""
        try:
            result = await self.db_session.execute(
                select(Sweet, SweetInventory)
                .outerjoin(SweetInventory, Sweet.id == SweetInventory.sweet_id)
                .where(Sweet.is_deleted == False)
                .order_by(Sweet.name)
            )
            return result.all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching sweets with inventory: {e}")
            raise DatabaseError(f"Failed to fetch sweets: {str(e)}")
    
    async def get_by_id(self, sweet_id: int) -> Optional[Sweet]:
        """Get sweet by ID with inventory and category"""
        try:
            result = await self.db_session.execute(
                select(Sweet)
                .options(
                    selectinload(Sweet.inventory),
                    selectinload(Sweet.category)
                )
                .where(Sweet.id == sweet_id, Sweet.is_deleted == False)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching sweet {sweet_id}: {e}")
            raise DatabaseError(f"Failed to fetch sweet: {str(e)}")
    
    async def is_available(self, sweet_id: int) -> bool:
        """Check if sweet exists and is not deleted"""
        try:
            result = await self.db_session.execute(
                select(func.count(Sweet.id))
                .where(Sweet.id == sweet_id, Sweet.is_deleted == False)
            )
            count = result.scalar()
            return count > 0
        except SQLAlchemyError as e:
            self.logger.error(f"Error checking sweet availability {sweet_id}: {e}")
            raise DatabaseError(f"Failed to check sweet availability: {str(e)}")
    
    async def get_inventory(self, sweet_id: int) -> Optional[SweetInventory]:
        """Get inventory for sweet"""
        try:
            result = await self.db_session.execute(
                select(SweetInventory)
                .where(SweetInventory.sweet_id == sweet_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching inventory for sweet {sweet_id}: {e}")
            raise DatabaseError(f"Failed to fetch inventory: {str(e)}")
    
    async def update_inventory(self, sweet_id: int, quantity_change: int) -> SweetInventory:
        """Update inventory quantity"""
        try:
            # First, check if inventory record exists
            existing_inventory = await self.get_inventory(sweet_id)
            
            if existing_inventory:
                # Update existing inventory
                new_quantity = existing_inventory.quantity + quantity_change
                if new_quantity < 0:
                    raise IntegrityConstraintError("Inventory quantity cannot be negative")
                
                result = await self.db_session.execute(
                    update(SweetInventory)
                    .where(SweetInventory.sweet_id == sweet_id)
                    .values(
                        quantity=new_quantity,
                        updated_at=datetime.utcnow()
                    )
                    .returning(SweetInventory)
                )
                
                updated_inventory = result.scalar_one()
                await self.db_session.flush()
                return updated_inventory
            
            else:
                # Create new inventory record
                if quantity_change < 0:
                    raise IntegrityConstraintError("Cannot create inventory with negative quantity")
                
                new_inventory = SweetInventory(
                    sweet_id=sweet_id,
                    quantity=quantity_change
                )
                self.db_session.add(new_inventory)
                await self.db_session.flush()
                await self.db_session.refresh(new_inventory)
                return new_inventory
                
        except IntegrityConstraintError:
            raise
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            self.logger.error(f"Error updating inventory for sweet {sweet_id}: {e}")
            raise DatabaseError(f"Failed to update inventory: {str(e)}")


class RestockRepository(IRestockRepository):
    """Concrete implementation of restock repository"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    async def create(self, admin_id: int, sweet_id: int, quantity_added: int) -> Restock:
        """Create restock record"""
        try:
            restock = Restock(
                admin_id=admin_id,
                sweet_id=sweet_id,
                quantity_added=quantity_added
            )
            
            self.db_session.add(restock)
            await self.db_session.flush()
            await self.db_session.refresh(restock)
            return restock
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            self.logger.error(f"Error creating restock: {e}")
            raise DatabaseError(f"Failed to create restock: {str(e)}")
    
    async def get_by_sweet_id(self, sweet_id: int, limit: Optional[int] = None) -> List[Restock]:
        """Get restock history for sweet"""
        try:
            query = (
                select(Restock)
                .options(selectinload(Restock.admin))
                .where(Restock.sweet_id == sweet_id)
                .order_by(Restock.restocked_at.desc())
            )
            
            if limit:
                query = query.limit(limit)
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching restock history for sweet {sweet_id}: {e}")
            raise DatabaseError(f"Failed to fetch restock history: {str(e)}")
    
    async def get_by_admin_id(self, admin_id: int, limit: Optional[int] = None) -> List[Restock]:
        """Get restock history by admin"""
        try:
            query = (
                select(Restock)
                .options(selectinload(Restock.sweet))
                .where(Restock.admin_id == admin_id)
                .order_by(Restock.restocked_at.desc())
            )
            
            if limit:
                query = query.limit(limit)
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching restock history for admin {admin_id}: {e}")
            raise DatabaseError(f"Failed to fetch admin restock history: {str(e)}")


# Repository Factory (Factory Pattern)

class RepositoryFactory:
    """Factory for creating repository instances"""
    
    @staticmethod
    def create_user_repository(db_session: AsyncSession) -> IUserRepository:
        """Create user repository"""
        return UserRepository(db_session)
    
    @staticmethod
    def create_sweet_repository(db_session: AsyncSession) -> ISweetRepository:
        """Create sweet repository"""
        return SweetRepository(db_session)
    
    @staticmethod
    def create_restock_repository(db_session: AsyncSession) -> IRestockRepository:
        """Create restock repository"""
        return RestockRepository(db_session)
    
    @staticmethod
    def create_all_repositories(db_session: AsyncSession) -> Dict[str, Any]:
        """Create all repositories"""
        return {
            'user_repo': UserRepository(db_session),
            'sweet_repo': SweetRepository(db_session),
            'restock_repo': RestockRepository(db_session)
        }
