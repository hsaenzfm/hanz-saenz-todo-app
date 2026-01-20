"""Integration tests for sorting functionality."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from todo.read.src.domain.models import (
    ListTodosQueryParams, 
    TodoReadProjection, 
    TodoSortField, 
    SortOrder
)
from todo.read.src.app.queries import list_todos_query
from todo.read.src.infra.repo import QueryFilters


class TestListTodosSorting:
    """Integration tests for sorting in list todos query."""

    @pytest.fixture
    def sample_todos_for_sorting(self):
        """Sample todo projections with different timestamps for sorting tests."""
        return [
            TodoReadProjection(
                id="todo-1",
                title="Oldest todo",
                description="Created first",
                status="pending",
                created_at="2026-01-18T08:00:00Z",  # Oldest
                updated_at="2026-01-18T08:00:00Z",
                due_date="2026-01-25",  # Middle due date
            ),
            TodoReadProjection(
                id="todo-2",
                title="Newest todo",
                description="Created last",
                status="pending",
                created_at="2026-01-20T10:00:00Z",  # Newest
                updated_at="2026-01-20T10:00:00Z",
                due_date="2026-01-23",  # Earliest due date
            ),
            TodoReadProjection(
                id="todo-3",
                title="Middle todo",
                description="Created in between",
                status="completed",
                created_at="2026-01-19T09:00:00Z",  # Middle
                updated_at="2026-01-19T09:00:00Z",
                due_date=None,  # No due date (should be last when sorting by due_date asc)
            ),
        ]

    @pytest.mark.asyncio
    async def test_sort_by_created_at_desc_default(self, sample_todos_for_sorting):
        """Test default sorting by created_at desc (newest first)."""
        # Sort todos newest first (default)
        sorted_todos = sorted(
            sample_todos_for_sorting, 
            key=lambda x: x.created_at, 
            reverse=True
        )
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (sorted_todos, 3)
            mock_get_repo.return_value = mock_repo

            # Use default parameters (should sort by created_at desc)
            params = ListTodosQueryParams()
            response = await list_todos_query(params)

            # Verify sorting - newest first
            assert len(response.data) == 3
            assert response.data[0].id == "todo-2"  # Newest (2026-01-20)
            assert response.data[1].id == "todo-3"  # Middle (2026-01-19)
            assert response.data[2].id == "todo-1"  # Oldest (2026-01-18)

            # Verify repository was called with correct sort parameters
            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.sort_field == "created_at"
            assert call_args.sort_order == "desc"

    @pytest.mark.asyncio
    async def test_sort_by_created_at_asc(self, sample_todos_for_sorting):
        """Test sorting by created_at asc (oldest first)."""
        # Sort todos oldest first
        sorted_todos = sorted(
            sample_todos_for_sorting, 
            key=lambda x: x.created_at, 
            reverse=False
        )
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (sorted_todos, 3)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(sort="created_at", order="asc")
            response = await list_todos_query(params)

            # Verify sorting - oldest first
            assert len(response.data) == 3
            assert response.data[0].id == "todo-1"  # Oldest (2026-01-18)
            assert response.data[1].id == "todo-3"  # Middle (2026-01-19)  
            assert response.data[2].id == "todo-2"  # Newest (2026-01-20)

            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.sort_field == "created_at"
            assert call_args.sort_order == "asc"

    @pytest.mark.asyncio
    async def test_sort_by_due_date_asc(self, sample_todos_for_sorting):
        """Test sorting by due_date asc (earliest due dates first, nulls last)."""
        # Sort by due_date with nulls last
        sorted_todos = sorted(
            sample_todos_for_sorting,
            key=lambda x: (x.due_date is None, x.due_date or ""),
            reverse=False
        )
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (sorted_todos, 3)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(sort="due_date", order="asc")
            response = await list_todos_query(params)

            # Verify sorting - earliest due dates first, nulls last
            assert len(response.data) == 3
            assert response.data[0].id == "todo-2"  # 2026-01-23 (earliest)
            assert response.data[1].id == "todo-1"  # 2026-01-25 (middle)
            assert response.data[2].id == "todo-3"  # None (nulls last)

            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.sort_field == "due_date"
            assert call_args.sort_order == "asc"

    @pytest.mark.asyncio
    async def test_sort_by_due_date_desc(self, sample_todos_for_sorting):
        """Test sorting by due_date desc (latest due dates first, nulls first)."""
        # Sort by due_date desc with nulls first 
        sorted_todos = sorted(
            sample_todos_for_sorting,
            key=lambda x: (x.due_date is None, x.due_date or ""),
            reverse=True
        )
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (sorted_todos, 3)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(sort="due_date", order="desc")
            response = await list_todos_query(params)

            # Verify sorting - nulls first when desc, then latest dates first
            assert len(response.data) == 3
            assert response.data[0].id == "todo-3"  # None (nulls first in desc)
            assert response.data[1].id == "todo-1"  # 2026-01-25 (latest)
            assert response.data[2].id == "todo-2"  # 2026-01-23 (earliest)

            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.sort_field == "due_date"
            assert call_args.sort_order == "desc"

    @pytest.mark.asyncio
    async def test_sort_with_status_filter(self, sample_todos_for_sorting):
        """Test sorting combined with status filtering."""
        # Filter for pending todos only, then sort
        pending_todos = [t for t in sample_todos_for_sorting if t.status == "pending"]
        sorted_pending = sorted(pending_todos, key=lambda x: x.created_at, reverse=True)
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (sorted_pending, 2)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                status="pending",
                sort="created_at", 
                order="desc"
            )
            response = await list_todos_query(params)

            # Verify only pending todos returned, sorted correctly
            assert len(response.data) == 2
            assert all(todo.status == "pending" for todo in response.data)
            assert response.data[0].id == "todo-2"  # Newest pending
            assert response.data[1].id == "todo-1"  # Older pending

            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.status == "pending"
            assert call_args.sort_field == "created_at"
            assert call_args.sort_order == "desc"

    @pytest.mark.asyncio
    async def test_sort_with_pagination(self, sample_todos_for_sorting):
        """Test sorting combined with pagination."""
        # Return only first item but indicate there are more
        sorted_todos = sorted(
            sample_todos_for_sorting, 
            key=lambda x: x.created_at, 
            reverse=True
        )
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = ([sorted_todos[0]], 3)  # Only first item
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                page=1,
                limit=1,
                sort="created_at",
                order="desc"
            )
            response = await list_todos_query(params)

            # Verify pagination works with sorting
            assert len(response.data) == 1
            assert response.data[0].id == "todo-2"  # First item from sorted list
            assert response.pagination.page == 1
            assert response.pagination.limit == 1
            assert response.pagination.total == 3
            assert response.pagination.totalPages == 3

    @pytest.mark.asyncio
    async def test_invalid_sort_field(self):
        """Test validation error for invalid sort field."""
        from todo.read.src.domain.exceptions import ValidationError

        params = ListTodosQueryParams(sort="invalid_field", order="desc")
        with pytest.raises(ValidationError) as exc_info:
            await list_todos_query(params)
        assert "sort must be one of [created_at, due_date]" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_sort_order(self):
        """Test validation error for invalid sort order."""
        from todo.read.src.domain.exceptions import ValidationError

        params = ListTodosQueryParams(sort="created_at", order="invalid_order")
        with pytest.raises(ValidationError) as exc_info:
            await list_todos_query(params)
        assert "order must be one of [asc, desc]" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_sort_enum_values(self):
        """Test that sort enums provide correct values."""
        assert TodoSortField.CREATED_AT.value == "created_at"
        assert TodoSortField.DUE_DATE.value == "due_date"
        assert set(TodoSortField.values()) == {"created_at", "due_date"}
        
        assert SortOrder.ASC.value == "asc"
        assert SortOrder.DESC.value == "desc"
        assert set(SortOrder.values()) == {"asc", "desc"}

    @pytest.mark.asyncio
    async def test_sort_criteria_model(self):
        """Test SortCriteria model validation."""
        from todo.read.src.domain.models import SortCriteria

        # Test valid criteria
        criteria = SortCriteria.create("created_at", "desc")
        assert criteria.field == "created_at"
        assert criteria.order == "desc"

        # Test default values
        criteria_default = SortCriteria.create()
        assert criteria_default.field == "created_at"
        assert criteria_default.order == "desc"

        # Test invalid field
        with pytest.raises(ValueError) as exc_info:
            SortCriteria("invalid_field", "desc")
        assert "Invalid sort field: invalid_field" in str(exc_info.value)

        # Test invalid order
        with pytest.raises(ValueError) as exc_info:
            SortCriteria("created_at", "invalid_order")
        assert "Invalid sort order: invalid_order" in str(exc_info.value)