"""Integration tests for status filtering functionality."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from todo.read.src.domain.models import ListTodosQueryParams, TodoReadProjection, TodoStatus
from todo.read.src.app.queries import list_todos_query
from todo.read.src.infra.repo import QueryFilters


class TestListTodosStatusFilter:
    """Integration tests for status filtering in list todos query."""

    @pytest.fixture
    def pending_todos(self):
        """Sample pending todo projections."""
        return [
            TodoReadProjection(
                id="pending-1",
                title="Complete project documentation",
                description="Write API documentation",
                status=TodoStatus.PENDING.value,
                created_at="2026-01-20T10:00:00Z",
                updated_at="2026-01-20T10:00:00Z",
                due_date="2026-01-25",
            ),
            TodoReadProjection(
                id="pending-2",
                title="Review code changes",
                description="Review pull request",
                status=TodoStatus.PENDING.value,
                created_at="2026-01-19T09:00:00Z",
                updated_at="2026-01-19T09:00:00Z",
                due_date=None,
            ),
        ]

    @pytest.fixture
    def completed_todos(self):
        """Sample completed todo projections."""
        return [
            TodoReadProjection(
                id="completed-1",
                title="Setup development environment",
                description="Install dependencies",
                status=TodoStatus.COMPLETED.value,
                created_at="2026-01-18T08:00:00Z",
                updated_at="2026-01-18T08:30:00Z",
                due_date="2026-01-20",
            ),
        ]

    @pytest.mark.asyncio
    async def test_filter_by_pending_status(self, pending_todos):
        """Test filtering todos by pending status."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (pending_todos, 2)
            mock_get_repo.return_value = mock_repo

            # Query for pending todos
            params = ListTodosQueryParams(page=1, limit=20, status="pending")
            response = await list_todos_query(params)

            # Verify response
            assert len(response.data) == 2
            assert all(todo.status == "pending" for todo in response.data)
            assert response.data[0].id == "pending-1"
            assert response.data[1].id == "pending-2"

            # Verify repository was called with correct filter
            mock_repo.list_todos.assert_called_once()
            call_args = mock_repo.list_todos.call_args[0][0]
            assert isinstance(call_args, QueryFilters)
            assert call_args.status == "pending"

    @pytest.mark.asyncio
    async def test_filter_by_completed_status(self, completed_todos):
        """Test filtering todos by completed status."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (completed_todos, 1)
            mock_get_repo.return_value = mock_repo

            # Query for completed todos
            params = ListTodosQueryParams(page=1, limit=20, status="completed")
            response = await list_todos_query(params)

            # Verify response
            assert len(response.data) == 1
            assert response.data[0].status == "completed"
            assert response.data[0].id == "completed-1"

            # Verify repository was called with correct filter
            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.status == "completed"

    @pytest.mark.asyncio
    async def test_no_status_filter_returns_all(self, pending_todos, completed_todos):
        """Test that not specifying status filter returns all todos."""
        all_todos = pending_todos + completed_todos
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (all_todos, 3)
            mock_get_repo.return_value = mock_repo

            # Query without status filter
            params = ListTodosQueryParams(page=1, limit=20)  # status=None (default)
            response = await list_todos_query(params)

            # Verify response contains both pending and completed
            assert len(response.data) == 3
            statuses = [todo.status for todo in response.data]
            assert "pending" in statuses
            assert "completed" in statuses

            # Verify repository was called with no status filter
            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.status is None

    @pytest.mark.asyncio
    async def test_status_filter_with_no_results(self):
        """Test status filter when no todos match the criteria."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = ([], 0)
            mock_get_repo.return_value = mock_repo

            # Query for pending todos but none exist
            params = ListTodosQueryParams(page=1, limit=20, status="pending")
            response = await list_todos_query(params)

            # Verify empty response
            assert len(response.data) == 0
            assert response.pagination.total == 0
            assert response.pagination.totalPages == 0

            # Verify correct filter was applied
            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.status == "pending"

    @pytest.mark.asyncio
    async def test_status_filter_with_pagination(self, pending_todos):
        """Test status filtering combined with pagination."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            # Simulate more pending todos exist but only one returned for this page
            mock_repo.list_todos.return_value = ([pending_todos[0]], 10)
            mock_get_repo.return_value = mock_repo

            # Query for pending todos with small limit
            params = ListTodosQueryParams(page=2, limit=1, status="pending")
            response = await list_todos_query(params)

            # Verify pagination works with filtering
            assert len(response.data) == 1
            assert response.data[0].status == "pending"
            assert response.pagination.page == 2
            assert response.pagination.limit == 1
            assert response.pagination.total == 10
            assert response.pagination.totalPages == 10

            # Verify correct filter and pagination
            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.status == "pending"
            assert call_args.page == 2
            assert call_args.limit == 1

    @pytest.mark.asyncio
    async def test_invalid_status_filter(self):
        """Test validation error for invalid status values."""
        from todo.read.src.domain.exceptions import ValidationError

        # Test invalid status value
        params = ListTodosQueryParams(page=1, limit=20, status="invalid_status")
        with pytest.raises(ValidationError) as exc_info:
            await list_todos_query(params)
        assert "status must be one of [pending, completed]" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_status_filter_case_sensitivity(self, pending_todos):
        """Test that status filtering is case sensitive."""
        from todo.read.src.domain.exceptions import ValidationError

        # Test uppercase status (should fail validation)
        params = ListTodosQueryParams(page=1, limit=20, status="PENDING")
        with pytest.raises(ValidationError) as exc_info:
            await list_todos_query(params)
        assert "status must be one of [pending, completed]" in str(exc_info.value)

        # Test mixed case status (should fail validation)
        params = ListTodosQueryParams(page=1, limit=20, status="Pending")
        with pytest.raises(ValidationError) as exc_info:
            await list_todos_query(params)
        assert "status must be one of [pending, completed]" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_status_enum_values(self):
        """Test that TodoStatus enum provides correct values."""
        assert TodoStatus.PENDING.value == "pending"
        assert TodoStatus.COMPLETED.value == "completed"
        assert set(TodoStatus.values()) == {"pending", "completed"}

    @pytest.mark.asyncio
    async def test_status_filter_combined_with_sorting(self, pending_todos):
        """Test status filtering combined with sorting parameters."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            # Return pending todos sorted by due_date
            sorted_todos = sorted(pending_todos, key=lambda x: x.due_date or "", reverse=True)
            mock_repo.list_todos.return_value = (sorted_todos, 2)
            mock_get_repo.return_value = mock_repo

            # Query for pending todos sorted by due_date desc
            params = ListTodosQueryParams(
                page=1, 
                limit=20, 
                status="pending", 
                sort="due_date", 
                order="desc"
            )
            response = await list_todos_query(params)

            # Verify both filtering and sorting were applied
            assert len(response.data) == 2
            assert all(todo.status == "pending" for todo in response.data)

            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.status == "pending"
            assert call_args.sort_field == "due_date"
            assert call_args.sort_order == "desc"