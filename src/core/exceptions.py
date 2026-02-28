"""
Custom exceptions for UI layer
"""


class DatabaseError(Exception):
    """Base exception for database operations"""
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a database record is not found"""
    pass


class RecordDeletedError(DatabaseError):
    """Raised when trying to access a deleted record"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""
    pass


class ValidationError(Exception):
    """Raised when data validation fails"""
    pass
