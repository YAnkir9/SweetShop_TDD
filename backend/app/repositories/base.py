"""
Base repository implementation following Repository pattern.
"""
from abc import ABC
from typing import Optional, List, Any, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase

from ..core.interfaces import IRepository
from ..core.exceptions import DatabaseError, NotFoundError

T = TypeVar('T', bound=DeclarativeBase)


class BaseRepository(IRepository, Generic[T]):
    """Base repository implementation with common CRUD operations."""
    
    def __init__(self, db: AsyncSession, model: type[T]):
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID."""
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseError(f"Failed to get {self.model.__name__} by ID: {str(e)}")
    
    async def create(self, entity_data: dict) -> T:
        """Create new entity."""
        try:
            entity = self.model(**entity_data)
            self.db.add(entity)
            await self.db.flush()  # Get ID without committing
            await self.db.refresh(entity)
            return entity
        except Exception as e:
            raise DatabaseError(f"Failed to create {self.model.__name__}: {str(e)}")
    
    async def update(self, id: Any, entity_data: dict) -> Optional[T]:
        """Update existing entity."""
        try:
            entity = await self.get_by_id(id)
            if not entity:
                raise NotFoundError(f"{self.model.__name__} not found")
            
            for key, value in entity_data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            await self.db.flush()
            await self.db.refresh(entity)
            return entity
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update {self.model.__name__}: {str(e)}")
    
    async def delete(self, id: Any) -> bool:
        """Delete entity by ID."""
        try:
            entity = await self.get_by_id(id)
            if not entity:
                return False
            
            await self.db.delete(entity)
            await self.db.flush()
            return True
        except Exception as e:
            raise DatabaseError(f"Failed to delete {self.model.__name__}: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        try:
            result = await self.db.execute(
                select(self.model).offset(skip).limit(limit)
            )
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseError(f"Failed to get all {self.model.__name__}: {str(e)}")
    
    async def count(self) -> int:
        """Count total entities."""
        try:
            from sqlalchemy import func
            result = await self.db.execute(
                select(func.count(self.model.id))
            )
            return result.scalar() or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count {self.model.__name__}: {str(e)}")
    
    async def exists(self, **filters) -> bool:
        """Check if entity exists with given filters."""
        try:
            query = select(self.model)
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise DatabaseError(f"Failed to check existence of {self.model.__name__}: {str(e)}")


class IUserRepository(ABC):
    """Interface for User repository operations."""
    
    async def get_by_email(self, email: str) -> Optional[Any]:
        pass
    
    async def get_by_username(self, username: str) -> Optional[Any]:
        pass
    
    async def get_with_role(self, user_id: int) -> Optional[Any]:
        pass


class IRoleRepository(ABC):
    """Interface for Role repository operations."""
    
    async def get_by_name(self, name: str) -> Optional[Any]:
        pass
    
    async def get_default_role(self) -> Any:
        pass


class ISweetRepository(ABC):
    """Interface for Sweet repository operations."""
    
    async def get_by_category(self, category_id: int) -> List[Any]:
        pass
    
    async def search_by_name(self, name: str) -> List[Any]:
        pass
    
    async def get_available_sweets(self) -> List[Any]:
        pass
