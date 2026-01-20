"""Exception classes for todo read service."""

from typing import Optional


class TodoReadServiceError(Exception):
    """Base exception for todo read service."""
    
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class ValidationError(TodoReadServiceError):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, error_code="INVALID_PARAMETER")


class DatabaseError(TodoReadServiceError):
    """Exception for database connection/query errors."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message, error_code="DATABASE_ERROR")


class NotFoundError(TodoReadServiceError):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, error_code="NOT_FOUND")


def create_error_response(error: TodoReadServiceError) -> dict:
    """Create standardized error response format.
    
    Args:
        error: The exception to format
        
    Returns:
        Dictionary with error response structure
    """
    response = {
        "error": {
            "code": error.error_code,
            "message": error.message
        }
    }
    
    # Add field information for validation errors
    if isinstance(error, ValidationError) and error.field:
        response["error"]["field"] = error.field
    
    return response