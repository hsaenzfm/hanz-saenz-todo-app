"""Repository interfaces and implementations for todo read service."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from dataclasses import dataclass
import psycopg
from psycopg.rows import class_row
import logging

from .config import get_database_config
from ..domain.exceptions import DatabaseError


@dataclass
class TodoReadProjection:
    """Todo read projection model."""
    
    id: str
    title: str
    description: Optional[str]
    status: str
    created_at: str  # ISO timestamp string
    updated_at: str  # ISO timestamp string
    due_date: Optional[str]  # ISO date string


@dataclass
class QueryFilters:
    """Query filters for listing todos."""
    
    status: Optional[str] = None
    sort_field: str = "created_at"
    sort_order: str = "desc"  # 'asc' or 'desc'
    page: int = 1
    limit: int = 20


class TodoReadRepository(ABC):
    """Abstract repository for todo read operations."""
    
    @abstractmethod
    async def list_todos(self, filters: QueryFilters) -> Tuple[List[TodoReadProjection], int]:
        """List todos with filtering, sorting, and pagination.
        
        Args:
            filters: Query filters including status, sort, pagination
            
        Returns:
            Tuple of (todos, total_count)
        """
        pass


class PostgresTodoReadRepository(TodoReadRepository):
    """PostgreSQL implementation of todo read repository."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize repository with database connection.
        
        Args:
            connection_string: PostgreSQL connection string. If None, will use config.
        """
        self._connection_string = connection_string or get_database_config().connection_string
    
    async def list_todos(self, filters: QueryFilters) -> Tuple[List[TodoReadProjection], int]:
        """List todos with filtering, sorting, and pagination.
        
        Args:
            filters: Query filters including status, sort, pagination
            
        Returns:
            Tuple of (todos, total_count)
            
        Raises:
            DatabaseError: If database connection or query fails
        """
        try:
            async with await psycopg.AsyncConnection.connect(
                self._connection_string,
                row_factory=class_row(TodoReadProjection)
            ) as conn:
                # Get total count for pagination
                total_count = await self._get_total_count(conn, filters)
                
                # Get paginated data
                todos = await self._get_todos_page(conn, filters)
                
                return todos, total_count
                
        except psycopg.OperationalError as e:
            logging.error(f"Database connection failed: {str(e)}")
            raise DatabaseError(
                "Database connection failed. Please try again later.",
                original_error=e
            )
        except psycopg.Error as e:
            logging.error(f"Database query failed: {str(e)}")
            raise DatabaseError(
                "Database query failed. Please check your request and try again.",
                original_error=e
            )
        except Exception as e:
            logging.error(f"Unexpected error in list_todos: {str(e)}")
            raise DatabaseError(
                "An unexpected database error occurred.",
                original_error=e
            )
    
    async def _get_total_count(
        self, 
        conn: psycopg.AsyncConnection, 
        filters: QueryFilters
    ) -> int:
        """Get total count of todos matching filters.
        
        Raises:
            DatabaseError: If query execution fails
        """
        count_query = """
            SELECT COUNT(*) 
            FROM todo_read_projection 
            WHERE deleted_at IS NULL 
              AND ($1::text IS NULL OR status = $1::text)
        """
        
        try:
            async with conn.cursor() as cur:
                await cur.execute(count_query, (filters.status,))
                result = await cur.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logging.error(f"Failed to get total count: {str(e)}")
            raise DatabaseError("Failed to count todos", original_error=e)
    
    async def _get_todos_page(
        self, 
        conn: psycopg.AsyncConnection, 
        filters: QueryFilters
    ) -> List[TodoReadProjection]:
        """Get paginated todos matching filters.
        
        Raises:
            DatabaseError: If query execution fails
        """
        # Calculate offset
        offset = (filters.page - 1) * filters.limit
        
        # Build the query with proper sorting
        base_query = """
            SELECT id, title, description, status, 
                   created_at, updated_at, due_date
            FROM todo_read_projection 
            WHERE deleted_at IS NULL 
              AND ($1::text IS NULL OR status = $1::text)
        """
        
        # Add ORDER BY clause based on sort parameters
        if filters.sort_field == "due_date":
            if filters.sort_order == "asc":
                order_clause = "ORDER BY due_date ASC NULLS LAST, created_at DESC"
            else:
                order_clause = "ORDER BY due_date DESC NULLS FIRST, created_at DESC"
        else:  # created_at
            if filters.sort_order == "asc":
                order_clause = "ORDER BY created_at ASC"
            else:
                order_clause = "ORDER BY created_at DESC"
        
        query = f"{base_query} {order_clause} LIMIT $2 OFFSET $3"
        
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    query, 
                    (filters.status, filters.limit, offset)
                )
                results = await cur.fetchall()
                
                # Convert to TodoReadProjection objects manually since psycopg class_row
                # might not work exactly as expected with async
                todos = []
                for row in results:
                    todo = TodoReadProjection(
                        id=str(row[0]),
                        title=row[1],
                        description=row[2],
                        status=row[3],
                        created_at=row[4].isoformat() if row[4] else "",
                        updated_at=row[5].isoformat() if row[5] else "",
                        due_date=row[6].isoformat() if row[6] else None,
                    )
                    todos.append(todo)
                
                return todos
        except Exception as e:
            logging.error(f"Failed to get todos page: {str(e)}")
            raise DatabaseError("Failed to fetch todos", original_error=e)


def get_todo_repository() -> TodoReadRepository:
    """Get todo read repository instance."""
    return PostgresTodoReadRepository()