from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Restock(Base):
    """Restock model for inventory management by admins"""
    __tablename__ = "restocks"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sweet_id = Column(Integer, ForeignKey("sweets.id"), nullable=False)
    quantity_added = Column(Integer, nullable=False)
    restocked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint('quantity_added > 0', name='check_quantity_added_positive'),
    )
    
    admin = relationship("User", back_populates="restocks")
    sweet = relationship("Sweet", back_populates="restocks")
    
    def __repr__(self):
        return f"<Restock(id={self.id}, admin_id={self.admin_id}, sweet_id={self.sweet_id}, quantity_added={self.quantity_added})>"
