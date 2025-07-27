"""Security utilities for input validation and sanitization"""

import re
from typing import Optional
from fastapi import HTTPException, status


def validate_user_input(text: Optional[str], field_name: str = "input") -> None:
    """
    Validate user input for potential security issues.
    
    This function demonstrates security awareness by checking for obvious 
    SQL injection patterns. Note that the primary protection comes from 
    using parameterized queries (SQLAlchemy ORM), not input validation.
    
    Args:
        text: The text input to validate
        field_name: Name of the field for error messages
        
    Raises:
        HTTPException: 400 if dangerous patterns are detected
    """
    if not text:
        return
    
    # Check for dangerous SQL injection patterns
    # Focus on the most obvious manipulation attempts
    dangerous_patterns = [
        r"\bUNION\s+SELECT\b",
        r"\bINSERT\s+INTO\b", 
        r"\bUPDATE\s+.*\s+SET\b",
        r"\bDELETE\s+FROM\b",
        r"\bCREATE\s+TABLE\b",
        r"\bALTER\s+TABLE\b",
        r"\bEXEC\b|\bEXECUTE\b"
    ]
    
    text_upper = text.upper()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_upper, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name} detected"
            )
