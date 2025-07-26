from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..database import Base
import uuid


class RevokedToken(Base):
    """Revoked token model for JWT token blacklisting"""
    __tablename__ = "revoked_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, nullable=False, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<RevokedToken(id={self.id}, jti='{self.jti}')>"
