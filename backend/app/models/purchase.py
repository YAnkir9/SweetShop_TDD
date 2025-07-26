from sqlalchemy import Column, Integer, ForeignKey, DateTime, DECIMAL, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Purchase(Base):
    """Purchase model for customer transactions"""
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sweet_id = Column(Integer, ForeignKey("sweets.id"), nullable=False)
    quantity_purchased = Column(Integer, nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    purchased_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint('quantity_purchased > 0', name='check_quantity_purchased_positive'),
        CheckConstraint('total_price >= 0', name='check_total_price_positive'),
    )
    
    user = relationship("User", back_populates="purchases")
    sweet = relationship("Sweet", back_populates="purchases")
    
    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, sweet_id={self.sweet_id}, quantity={self.quantity_purchased})>"
