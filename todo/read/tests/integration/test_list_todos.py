"""Integration tests for list todos functionality."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from todo.read.src.domain.models import ListTodosQueryParams, TodoReadProjection
from todo.read.src.app.queries import list_todos_query
from todo.read.src.infra.repo import QueryFilters


class TestListTodosIntegration:
    """Integration tests for list todos query."""

    @pytest.fixture
    def sample_todos(self):
        """Sample todo projections for testing."""
        return [
            TodoReadProjection(
                id="123e4567-e89b-12d3-a456-426614174000",
                title="Complete project documentation",
                description="Write API documentation",
                status="pending",
                created_at="2026-01-20T10:00:00Z",
                updated_at="2026-01-20T10:00:00Z",
                due_date="2026-01-25",
            ),
            TodoReadProjection(
                id="123e4567-e89b-12d3-a456-426614174001",
                title="Review code changes",
                description="Review pull request",
                status="completed",
                created_at="2026-01-19T09:00:00Z",
                updated_at="2026-01-19T09:00:00Z",
                due_date=None,
            ),
        ]

    @pytest.mark.asyncio
    async def test_list_todos_basic_pagination(self, sample_todos):
        """Test basic pagination functionality."""
        # Mock the repository
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (sample_todos, 2)
            mock_get_repo.return_value = mock_repo

            # Create query parameters
            params = ListTodosQueryParams(page=1, limit=20)

            # Execute query
            response = await list_todos_query(params)

            # Verify response structure
            assert response is not None
            assert hasattr(response, 'data')
            assert hasattr(response, 'pagination')

            # Verify data
            assert len(response.data) == 2
            assert response.data[0].id == "123e4567-e89b-12d3-a456-426614174000"
            assert response.data[0].title == "Complete project documentation"
            assert response.data[1].id == "123e4567-e89b-12d3-a456-426614174001"
            assert response.data[1].title == "Review code changes"

            # Verify pagination
            assert response.pagination.page == 1
            assert response.pagination.limit == 20
            assert response.pagination.total == 2
            assert response.pagination.totalPages == 1

            # Verify repository was called correctly
            mock_repo.list_todos.assert_called_once()
            call_args = mock_repo.list_todos.call_args[0][0]
            assert isinstance(call_args, QueryFilters)
            assert call_args.page == 1
            assert call_args.limit == 20
            assert call_args.status is None
            assert call_args.sort_field == "created_at"
            assert call_args.sort_order == "desc"

    @pytest.mark.asyncio
    async def test_list_todos_empty_result(self):
        """Test pagination with empty result set."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = ([], 0)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(page=1, limit=20)
            response = await list_todos_query(params)

            # Verify empty response
            assert len(response.data) == 0
            assert response.pagination.page == 1
            assert response.pagination.limit == 20
            assert response.pagination.total == 0
            assert response.pagination.totalPages == 0

    @pytest.mark.asyncio
    async def test_list_todos_second_page(self, sample_todos):
        """Test requesting second page."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            # Return only first todo for second page
            mock_repo.list_todos.return_value = ([sample_todos[0]], 25)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(page=2, limit=20)
            response = await list_todos_query(params)

            # Verify pagination calculation
            assert response.pagination.page == 2
            assert response.pagination.limit == 20
            assert response.pagination.total == 25
            assert response.pagination.totalPages == 2  # ceil(25/20) = 2

            # Verify repository was called with correct offset
            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.page == 2
            assert call_args.limit == 20

    @pytest.mark.asyncio
    async def test_list_todos_with_custom_limit(self, sample_todos):
        """Test pagination with custom limit."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = ([sample_todos[0]], 10)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(page=1, limit=5)
            response = await list_todos_query(params)

            # Verify pagination with smaller limit
            assert response.pagination.limit == 5
            assert response.pagination.total == 10
            assert response.pagination.totalPages == 2  # ceil(10/5) = 2

            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.limit == 5

    @pytest.mark.asyncio
    async def test_list_todos_data_conversion(self, sample_todos):
        """Test conversion from projection to response items."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (sample_todos, 2)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams()
            response = await list_todos_query(params)

            # Verify all fields are properly converted
            todo_item = response.data[0]
            projection = sample_todos[0]
            
            assert todo_item.id == projection.id
            assert todo_item.title == projection.title
            assert todo_item.description == projection.description
            assert todo_item.status == projection.status
            assert todo_item.created_at == projection.created_at
            assert todo_item.updated_at == projection.updated_at
            assert todo_item.due_date == projection.due_date

    @pytest.mark.asyncio
    async def test_list_todos_validation_error(self):
        """Test that validation errors are properly raised."""
        from todo.read.src.domain.exceptions import ValidationError
        
        # Test invalid page
        params = ListTodosQueryParams(page=0, limit=20)
        with pytest.raises(ValidationError) as exc_info:
            await list_todos_query(params)
        assert "page must be >= 1" in str(exc_info.value)

        # Test invalid limit
        params = ListTodosQueryParams(page=1, limit=101)
        with pytest.raises(ValidationError) as exc_info:
            await list_todos_query(params)
        assert "limit must be <= 100" in str(exc_info.value)

        # Test invalid status
        params = ListTodosQueryParams(page=1, limit=20, status="invalid")
        with pytest.raises(ValidationError) as exc_info:
            await list_todos_query(params)
        assert "status must be one of [pending, completed]" in str(exc_info.value)