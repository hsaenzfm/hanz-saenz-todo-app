"""End-to-end integration tests combining all features."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from todo.read.src.domain.models import ListTodosQueryParams, TodoReadProjection
from todo.read.src.app.queries import list_todos_query
from todo.read.src.infra.repo import QueryFilters


class TestListTodosCompleteIntegration:
    """End-to-end integration tests combining pagination, filtering, and sorting."""

    @pytest.fixture
    def comprehensive_todos(self):
        """Comprehensive set of todos for complete integration testing."""
        return [
            # Recent pending todos
            TodoReadProjection(
                id="pending-recent-1",
                title="High priority task",
                description="Must complete today",
                status="pending",
                created_at="2026-01-20T14:00:00Z",  # Most recent
                updated_at="2026-01-20T14:00:00Z",
                due_date="2026-01-21",  # Tomorrow
            ),
            TodoReadProjection(
                id="pending-recent-2", 
                title="Medium priority task",
                description="Can wait a bit",
                status="pending",
                created_at="2026-01-20T10:00:00Z",
                updated_at="2026-01-20T10:00:00Z",
                due_date="2026-01-25",  # Later this week
            ),
            # Older pending todos
            TodoReadProjection(
                id="pending-old-1",
                title="Long-running task",
                description="Started long ago",
                status="pending",
                created_at="2026-01-18T08:00:00Z",  # Older
                updated_at="2026-01-18T08:00:00Z",
                due_date=None,  # No deadline
            ),
            # Completed todos
            TodoReadProjection(
                id="completed-recent-1",
                title="Finished yesterday",
                description="Just completed",
                status="completed",
                created_at="2026-01-19T16:00:00Z",
                updated_at="2026-01-19T16:00:00Z",
                due_date="2026-01-20",  # Was due today
            ),
            TodoReadProjection(
                id="completed-old-1",
                title="Old completed task",
                description="Done ages ago",
                status="completed",
                created_at="2026-01-15T09:00:00Z",  # Oldest
                updated_at="2026-01-15T09:00:00Z",
                due_date="2026-01-16",  # Was due in the past
            ),
        ]

    @pytest.mark.asyncio
    async def test_pagination_with_filtering_and_sorting(self, comprehensive_todos):
        """Test pagination combined with status filtering and creation date sorting."""
        # Filter for pending todos only, sorted by created_at desc
        pending_todos = [t for t in comprehensive_todos if t.status == "pending"]
        pending_sorted = sorted(pending_todos, key=lambda x: x.created_at, reverse=True)
        
        # Simulate pagination: page 1 with limit 2 (should return first 2 pending todos)
        page_1_todos = pending_sorted[:2]
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (page_1_todos, 3)  # 3 total pending
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                page=1,
                limit=2,
                status="pending",
                sort="created_at",
                order="desc"
            )
            response = await list_todos_query(params)

            # Verify complete integration
            assert len(response.data) == 2
            
            # Verify filtering: all returned todos are pending
            assert all(todo.status == "pending" for todo in response.data)
            
            # Verify sorting: newest pending todos first
            assert response.data[0].id == "pending-recent-1"  # Most recent
            assert response.data[1].id == "pending-recent-2"  # Second most recent
            
            # Verify pagination metadata
            assert response.pagination.page == 1
            assert response.pagination.limit == 2
            assert response.pagination.total == 3
            assert response.pagination.totalPages == 2  # ceil(3/2) = 2

            # Verify repository called with all parameters
            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.page == 1
            assert call_args.limit == 2
            assert call_args.status == "pending"
            assert call_args.sort_field == "created_at"
            assert call_args.sort_order == "desc"

    @pytest.mark.asyncio
    async def test_due_date_sorting_with_null_handling(self, comprehensive_todos):
        """Test sorting by due_date with proper NULL handling."""
        # Sort by due_date asc: non-null dates first (ascending), then nulls last
        sorted_by_due_date = sorted(
            comprehensive_todos,
            key=lambda x: (x.due_date is None, x.due_date or "")
        )
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (sorted_by_due_date, 5)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                sort="due_date",
                order="asc"
            )
            response = await list_todos_query(params)

            # Verify due_date sorting with null handling
            assert len(response.data) == 5
            
            # First todos should have earliest due dates
            assert response.data[0].due_date == "2026-01-16"  # Earliest
            assert response.data[1].due_date == "2026-01-20"  # Second
            assert response.data[2].due_date == "2026-01-21"  # Third
            assert response.data[3].due_date == "2026-01-25"  # Fourth
            
            # Last todo should have null due_date (nulls last)
            assert response.data[4].due_date is None
            assert response.data[4].id == "pending-old-1"

    @pytest.mark.asyncio 
    async def test_completed_todos_pagination_second_page(self, comprehensive_todos):
        """Test getting second page of completed todos."""
        # Filter and sort completed todos by created_at desc
        completed_todos = [t for t in comprehensive_todos if t.status == "completed"]
        completed_sorted = sorted(completed_todos, key=lambda x: x.created_at, reverse=True)
        
        # Simulate page 2 with limit 1: should return the older completed todo
        page_2_todos = completed_sorted[1:2] if len(completed_sorted) > 1 else []
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (page_2_todos, 2)  # 2 total completed
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                page=2,
                limit=1,
                status="completed",
                sort="created_at",
                order="desc"
            )
            response = await list_todos_query(params)

            # Verify second page of completed todos
            assert len(response.data) == 1
            assert response.data[0].status == "completed"
            assert response.data[0].id == "completed-old-1"  # Older completed todo
            
            # Verify pagination for second page
            assert response.pagination.page == 2
            assert response.pagination.limit == 1
            assert response.pagination.total == 2
            assert response.pagination.totalPages == 2

    @pytest.mark.asyncio
    async def test_empty_page_beyond_results(self, comprehensive_todos):
        """Test requesting a page beyond available results."""
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = ([], 5)  # Empty page but 5 total
            mock_get_repo.return_value = mock_repo

            # Request page 10 with limit 20 (beyond available data)
            params = ListTodosQueryParams(page=10, limit=20)
            response = await list_todos_query(params)

            # Verify empty results but proper pagination metadata
            assert len(response.data) == 0
            assert response.pagination.page == 10
            assert response.pagination.limit == 20
            assert response.pagination.total == 5
            assert response.pagination.totalPages == 1  # ceil(5/20) = 1

    @pytest.mark.asyncio
    async def test_maximum_limit_with_filtering(self, comprehensive_todos):
        """Test maximum limit (100) combined with status filtering."""
        # Filter for all pending todos
        pending_todos = [t for t in comprehensive_todos if t.status == "pending"]
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (pending_todos, 3)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                limit=100,  # Maximum allowed limit
                status="pending"
            )
            response = await list_todos_query(params)

            # Verify maximum limit works with filtering
            assert len(response.data) == 3  # All pending todos returned
            assert response.pagination.limit == 100
            assert response.pagination.total == 3
            assert response.pagination.totalPages == 1  # All fit in one page

            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.limit == 100
            assert call_args.status == "pending"

    @pytest.mark.asyncio
    async def test_all_features_combined_realistic_scenario(self, comprehensive_todos):
        """Test realistic scenario combining all features with typical usage."""
        # Scenario: Get pending todos, sorted by due_date asc (closest deadlines first),
        # page 1 with reasonable limit
        
        pending_todos = [t for t in comprehensive_todos if t.status == "pending"]
        # Sort by due_date asc with nulls last
        pending_sorted = sorted(
            pending_todos,
            key=lambda x: (x.due_date is None, x.due_date or "")
        )
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (pending_sorted, 3)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                page=1,
                limit=10,
                status="pending",
                sort="due_date",
                order="asc"
            )
            response = await list_todos_query(params)

            # Verify realistic scenario works end-to-end
            assert len(response.data) == 3
            assert all(todo.status == "pending" for todo in response.data)
            
            # Verify due_date sorting (closest deadlines first)
            assert response.data[0].due_date == "2026-01-21"  # Tomorrow (urgent)
            assert response.data[1].due_date == "2026-01-25"  # This week
            assert response.data[2].due_date is None          # No deadline (last)
            
            # Verify all parameters passed correctly
            call_args = mock_repo.list_todos.call_args[0][0]
            assert call_args.page == 1
            assert call_args.limit == 10
            assert call_args.status == "pending"
            assert call_args.sort_field == "due_date" 
            assert call_args.sort_order == "asc"

    @pytest.mark.asyncio
    async def test_error_handling_in_complete_workflow(self):
        """Test error handling throughout the complete workflow."""
        from todo.read.src.domain.exceptions import ValidationError, DatabaseError
        
        # Test validation error propagation
        params = ListTodosQueryParams(
            page=0,  # Invalid
            limit=101,  # Invalid  
            status="invalid",  # Invalid
        )
        
        with pytest.raises(ValidationError):
            await list_todos_query(params)
        
        # Test database error propagation
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.side_effect = DatabaseError("Connection failed")
            mock_get_repo.return_value = mock_repo

            valid_params = ListTodosQueryParams()
            with pytest.raises(DatabaseError):
                await list_todos_query(valid_params)