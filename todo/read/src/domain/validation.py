"""Validation logic for todo read service."""

from typing import List, Optional
from .models import ListTodosQueryParams, TodoStatus, TodoSortField, SortOrder
from .exceptions import ValidationError


def validate_pagination_params(page: int, limit: int) -> List[str]:
    """Validate pagination parameters.
    
    Args:
        page: Page number (1-based)
        limit: Items per page
        
    Returns:
        List of validation error messages. Empty list if valid.
    """
    errors = []
    
    if page < 1:
        errors.append("page must be >= 1")
        
    if limit < 1:
        errors.append("limit must be >= 1")
        
    if limit > 100:
        errors.append("limit must be <= 100")
        
    return errors


def validate_status_filter(status: Optional[str]) -> List[str]:
    """Validate status filter parameter.
    
    Args:
        status: Status filter value
        
    Returns:
        List of validation error messages. Empty list if valid.
    """
    errors = []
    
    if status is not None and status not in TodoStatus.values():
        errors.append("status must be one of [pending, completed]")
        
    return errors


def validate_sort_params(sort_field: str, sort_order: str) -> List[str]:
    """Validate sort parameters.
    
    Args:
        sort_field: Field to sort by
        sort_order: Sort direction
        
    Returns:
        List of validation error messages. Empty list if valid.
    """
    errors = []
    
    if sort_field not in TodoSortField.values():
        errors.append("sort must be one of [created_at, due_date]")
        
    if sort_order not in SortOrder.values():
        errors.append("order must be one of [asc, desc]")
        
    return errors


def validate_list_todos_params(params: ListTodosQueryParams) -> None:
    """Validate all list todos query parameters.
    
    Args:
        params: Query parameters to validate
        
    Raises:
        ValidationError: If any parameter is invalid
    """
    all_errors = []
    
    # Validate pagination
    all_errors.extend(validate_pagination_params(params.page, params.limit))
    
    # Validate status filter
    all_errors.extend(validate_status_filter(params.status))
    
    # Validate sort parameters  
    all_errors.extend(validate_sort_params(params.sort, params.order))
    
    if all_errors:
        # Return the first error for simplicity
        raise ValidationError(f"Invalid parameter: {all_errors[0]}")


def validate_integer_param(value: str, param_name: str, min_value: int = None, max_value: int = None) -> int:
    """Validate and convert string parameter to integer.
    
    Args:
        value: String value to convert
        param_name: Parameter name for error messages
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)
        
    Returns:
        Converted integer value
        
    Raises:
        ValidationError: If value is invalid
    """
    try:
        int_value = int(value)
    except ValueError:
        raise ValidationError(f"Invalid parameter: {param_name} must be a valid integer", field=param_name)
    
    if min_value is not None and int_value < min_value:
        raise ValidationError(f"Invalid parameter: {param_name} must be >= {min_value}", field=param_name)
        
    if max_value is not None and int_value > max_value:
        raise ValidationError(f"Invalid parameter: {param_name} must be <= {max_value}", field=param_name)
    
    return int_value