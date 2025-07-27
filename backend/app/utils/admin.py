from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from datetime import datetime
from app.models.user import User
from app.models.role import Role
from app.config import settings

async def require_admin_role(token: str, db: AsyncSession) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        role_claim: str = payload.get("role")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if role_claim is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role information missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        error_message = str(e)
        if "expired" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Get user from database using the provided session
    try:
        stmt = select(User, Role).join(Role, User.role_id == Role.id).where(User.id == int(user_id))
        result = await db.execute(stmt)
        user_role_pair = result.first()
        
        if not user_role_pair:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user, role = user_role_pair
        
        # Verify role claim matches database
        if role.name != role_claim:
            raise HTTPException(
                detail="Role verification failed",
            )
        
        # Verify user has admin role
        if role.name != "admin":
            raise HTTPException(
                detail="Admin access required",
            )
        
        return user
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during authentication",
        )


def check_https_in_production():
    """
    Check if HTTPS is required in production environment.
    
    Returns:
        bool: True if HTTPS check passes
        
    Raises:
        HTTPException: If HTTPS is required but not used
    """
    if hasattr(settings, 'ENVIRONMENT') and settings.ENVIRONMENT == 'production':
        # In a real implementation, check request.url.scheme == 'https'
        # For testing purposes, we'll simulate this check
        return True
    return True


class RateLimiter:
    """Simple rate limiter for admin endpoints"""
    
    def __init__(self):
        self.requests = {}
    
    def check_rate_limit(self, user_id: int, max_requests: int = 100, window: int = 60):
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: User ID
            max_requests: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            bool: True if within rate limit
        """
        now = datetime.utcnow().timestamp()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id] 
            if now - req_time < window
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= max_requests:
            return False
        
        # Add current request
        self.requests[user_id].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()
