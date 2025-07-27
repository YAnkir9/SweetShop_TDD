from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Sweet(Base):
    __tablename__ = "sweets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    image_url = Column(String(500))
    description = Column(String(1000))
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
    )
    
    category = relationship("Category", back_populates="sweets")
    inventory = relationship("SweetInventory", back_populates="sweet", uselist=False)
    purchases = relationship("Purchase", back_populates="sweet")
    reviews = relationship("Review", back_populates="sweet")
    restocks = relationship("Restock", back_populates="sweet")
    
    def __repr__(self):
        return f"<Sweet(id={self.id}, name='{self.name}', price={self.price})>"
