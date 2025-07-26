from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Review(Base):
    """Review model for sweet ratings and comments"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sweet_id = Column(Integer, ForeignKey("sweets.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        UniqueConstraint('user_id', 'sweet_id', name='unique_user_sweet_review'),
    )
    
    user = relationship("User", back_populates="reviews")
    sweet = relationship("Sweet", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, sweet_id={self.sweet_id}, rating={self.rating})>"
