"""Query handlers for todo read service."""

import time
from typing import List
from ..domain.models import (
    ListTodosQueryParams, 
    ListTodosResponse, 
    PaginationMetadata,
    TodoItem,
    TodoReadProjection,
)
from ..domain.validation import validate_list_todos_params
from ..domain.exceptions import DatabaseError
from ..infra.repo import get_todo_repository, QueryFilters
from ..infra.logging import log_query_performance, log_database_error


async def list_todos_query(params: ListTodosQueryParams) -> ListTodosResponse:
    """List todos with pagination, filtering, and sorting.
    
    Args:
        params: Query parameters including pagination, filters, and sort options
        
    Returns:
        ListTodosResponse with todos and pagination metadata
        
    Raises:
        ValidationError: If parameters are invalid
        DatabaseError: If database query fails
    """
    # Validate parameters
    validate_list_todos_params(params)
    
    # Convert to repository filters
    filters = QueryFilters(
        status=params.status,
        sort_field=params.sort,
        sort_order=params.order,
        page=params.page,
        limit=params.limit,
    )
    
    # Execute query with performance tracking
    start_time = time.time()
    try:
        repository = get_todo_repository()
        projections, total_count = await repository.list_todos(filters)
        
        # Log performance
        duration_ms = (time.time() - start_time) * 1000
        log_query_performance(
            query_name="list_todos",
            duration_ms=duration_ms,
            record_count=len(projections),
            filters={
                "status": params.status,
                "sort": params.sort,
                "order": params.order,
                "page": params.page,
                "limit": params.limit,
            }
        )
        
        # Convert projections to response items
        todos = [_projection_to_item(p) for p in projections]
        
        # Create pagination metadata
        pagination = PaginationMetadata.create(
            page=params.page,
            limit=params.limit,
            total=total_count,
        )
        
        return ListTodosResponse(
            data=todos,
            pagination=pagination,
        )
        
    except Exception as e:
        # Log database errors
        log_database_error(e)
        raise DatabaseError(f"Failed to list todos: {str(e)}", original_error=e)


def _projection_to_item(projection: TodoReadProjection) -> TodoItem:
    """Convert TodoReadProjection to TodoItem for API response.
    
    Args:
        projection: Database projection object
        
    Returns:
        TodoItem for API response
    """
    return TodoItem(
        id=projection.id,
        title=projection.title,
        description=projection.description,
        status=projection.status,
        created_at=projection.created_at,
        updated_at=projection.updated_at,
        due_date=projection.due_date,
    )


# Synchronous wrapper for Lambda integration
def list_todos_query_sync(params: ListTodosQueryParams) -> ListTodosResponse:
    """Synchronous wrapper for list_todos_query.
    
    This is a temporary implementation for Lambda integration.
    In a real implementation, you would use asyncio.run() or similar.
    
    Args:
        params: Query parameters
        
    Returns:
        ListTodosResponse with todos and pagination metadata
    """
    import asyncio
    
    try:
        # Use asyncio.run for sync wrapper
        return asyncio.run(list_todos_query(params))
    except Exception as e:
        # Re-raise for proper error handling at API layer
        raise e