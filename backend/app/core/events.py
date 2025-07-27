"""
Domain events for the application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from .interfaces import IDomainEvent


@dataclass
class UserRegisteredEvent(IDomainEvent):
    """Event raised when a user registers."""
    
    user_id: int
    email: str
    username: str
    timestamp: datetime
    
    @property
    def event_type(self) -> str:
        return "user.registered"
    
    @property
    def payload(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class UserLoginEvent(IDomainEvent):
    """Event raised when a user logs in."""
    
    user_id: int
    email: str
    timestamp: datetime
    ip_address: str = None
    
    @property
    def event_type(self) -> str:
        return "user.login"
    
    @property
    def payload(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address
        }


@dataclass
class AdminActionEvent(IDomainEvent):
    """Event raised when an admin performs an action."""
    
    admin_id: int
    action: str
    details: Dict[str, Any]
    timestamp: datetime
    
    @property
    def event_type(self) -> str:
        return "admin.action"
    
    @property
    def payload(self) -> Dict[str, Any]:
        return {
            "admin_id": self.admin_id,
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class InventoryUpdatedEvent(IDomainEvent):
    """Event raised when inventory is updated."""
    
    sweet_id: int
    quantity_change: int
    updated_by: int
    timestamp: datetime
    
    @property
    def event_type(self) -> str:
        return "inventory.updated"
    
    @property
    def payload(self) -> Dict[str, Any]:
        return {
            "sweet_id": self.sweet_id,
            "quantity_change": self.quantity_change,
            "updated_by": self.updated_by,
            "timestamp": self.timestamp.isoformat()
        }
