"""
Authentication utilities - NOT IMPLEMENTED YET (TDD RED CASE)
"""
from passlib.context import CryptContext
from passlib.hash import bcrypt
from typing import Union


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt - NOT IMPLEMENTED YET (TDD RED CASE)
    """
    # TODO: Implement password hashing
    raise NotImplementedError("Password hashing not implemented yet")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash - NOT IMPLEMENTED YET (TDD RED CASE)
    """
    # TODO: Implement password verification
    raise NotImplementedError("Password verification not implemented yet")


def get_password_hash(password: str) -> str:
    """
    Alternative function name for password hashing - NOT IMPLEMENTED YET (TDD RED CASE)
    """
    # TODO: Implement password hashing
    raise NotImplementedError("Password hashing not implemented yet")
