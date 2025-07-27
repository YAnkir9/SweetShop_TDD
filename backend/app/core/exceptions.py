"""
Custom exceptions for the application following clean architecture.
"""


class SweetShopException(Exception):
    """Base exception for all application-specific errors."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(SweetShopException):
    """Raised when validation fails."""
    pass


class NotFoundError(SweetShopException):
    """Raised when a resource is not found."""
    pass


class ConflictError(SweetShopException):
    """Raised when there's a conflict in the operation."""
    pass


class UnauthorizedError(SweetShopException):
    """Raised when authentication fails."""
    pass


class ForbiddenError(SweetShopException):
    """Raised when authorization fails."""
    pass


class DatabaseError(SweetShopException):
    """Raised when database operations fail."""
    pass


class TokenError(SweetShopException):
    """Raised when token operations fail."""
    pass


class BusinessRuleError(SweetShopException):
    """Raised when business rules are violated."""
    pass


class ExternalServiceError(SweetShopException):
    """Raised when external service calls fail."""
    pass


class CacheError(SweetShopException):
    """Raised when cache operations fail."""
    pass
