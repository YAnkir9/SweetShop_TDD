from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class SweetInventory(Base):
    """Inventory model for sweet stock management"""
    __tablename__ = "sweet_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    sweet_id = Column(Integer, ForeignKey("sweets.id"), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_quantity_positive'),
    )
    
    sweet = relationship("Sweet", back_populates="inventory")
    
    def __repr__(self):
        return f"<SweetInventory(id={self.id}, sweet_id={self.sweet_id}, quantity={self.quantity})>"
