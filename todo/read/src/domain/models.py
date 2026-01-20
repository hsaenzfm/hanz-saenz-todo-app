"""Domain models for todo read service."""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import math


class TodoStatus(Enum):
    """Enumeration for todo status values."""
    
    PENDING = "pending"
    COMPLETED = "completed"
    
    @classmethod
    def values(cls) -> List[str]:
        """Get list of valid status values."""
        return [status.value for status in cls]


class TodoSortField(Enum):
    """Enumeration for todo sort field values."""
    
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"
    
    @classmethod
    def values(cls) -> List[str]:
        """Get list of valid sort field values."""
        return [field.value for field in cls]


class SortOrder(Enum):
    """Enumeration for sort order values."""
    
    ASC = "asc"
    DESC = "desc"
    
    @classmethod
    def values(cls) -> List[str]:
        """Get list of valid sort order values."""
        return [order.value for order in cls]


@dataclass
class SortCriteria:
    """Sort criteria for todo queries."""
    
    field: str
    order: str
    
    def __post_init__(self):
        """Validate sort criteria after initialization."""
        if self.field not in TodoSortField.values():
            raise ValueError(f"Invalid sort field: {self.field}")
        if self.order not in SortOrder.values():
            raise ValueError(f"Invalid sort order: {self.order}")
    
    @classmethod
    def create(cls, field: str = "created_at", order: str = "desc") -> "SortCriteria":
        """Create sort criteria with defaults.
        
        Args:
            field: Sort field (default: created_at)
            order: Sort order (default: desc)
            
        Returns:
            SortCriteria instance
        """
        return cls(field=field, order=order)


@dataclass
class TodoReadProjection:
    """Read-side projection of a todo, optimized for querying."""
    
    id: str
    title: str
    description: Optional[str]
    status: str  # 'pending' or 'completed'
    created_at: str  # ISO timestamp string
    updated_at: str  # ISO timestamp string
    due_date: Optional[str]  # ISO date string or None


@dataclass
class PaginationMetadata:
    """Metadata about pagination state for list query responses."""
    
    page: int
    limit: int
    total: int
    totalPages: int
    
    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationMetadata":
        """Create pagination metadata with calculated totalPages.
        
        Args:
            page: Current page number (1-based)
            limit: Number of items per page
            total: Total count of items matching filters
            
        Returns:
            PaginationMetadata instance
        """
        total_pages = math.ceil(total / limit) if total > 0 else 0
        return cls(
            page=page,
            limit=limit,
            total=total,
            totalPages=total_pages,
        )


@dataclass
class TodoItem:
    """Todo item for API responses."""
    
    id: str
    title: str
    description: Optional[str]
    status: str
    created_at: str
    updated_at: str
    due_date: Optional[str]


@dataclass
class ListTodosResponse:
    """Response structure for the list todos endpoint."""
    
    data: List[TodoItem]
    pagination: PaginationMetadata


@dataclass
class ListTodosQueryParams:
    """Query parameters for the list todos endpoint."""
    
    page: int = 1
    limit: int = 20
    status: Optional[str] = None
    sort: str = "created_at"
    order: str = "desc"
    
    def validate(self) -> List[str]:
        """Validate query parameters.
        
        Returns:
            List of validation error messages. Empty list if valid.
        """
        errors = []
        
        if self.page < 1:
            errors.append("page must be >= 1")
            
        if self.limit < 1 or self.limit > 100:
            errors.append("limit must be between 1 and 100")
            
        if self.status is not None and self.status not in ["pending", "completed"]:
            errors.append("status must be one of [pending, completed]")
            
        if self.sort not in ["created_at", "due_date"]:
            errors.append("sort must be one of [created_at, due_date]")
            
        if self.order not in ["asc", "desc"]:
            errors.append("order must be one of [asc, desc]")
            
        return errors