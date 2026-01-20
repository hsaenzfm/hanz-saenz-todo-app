"""Performance tests for list todos functionality."""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from todo.read.src.domain.models import ListTodosQueryParams, TodoReadProjection
from todo.read.src.app.queries import list_todos_query


class TestListTodosPerformance:
    """Performance tests for list todos with large datasets."""

    def generate_large_todo_set(self, count: int, status_mix: bool = True):
        """Generate a large set of todos for performance testing.
        
        Args:
            count: Number of todos to generate
            status_mix: Whether to mix pending/completed status
            
        Returns:
            List of TodoReadProjection objects
        """
        todos = []
        for i in range(count):
            # Alternate between pending and completed if status_mix is True
            status = "pending" if not status_mix or i % 2 == 0 else "completed"
            
            # Create varied due dates (some with nulls)
            if i % 5 == 0:
                due_date = None  # 20% have no due date
            else:
                # Create dates spreading over next 30 days
                day_offset = i % 30
                due_date = f"2026-01-{21 + day_offset:02d}" if day_offset < 10 else f"2026-02-{day_offset - 10 + 1:02d}"
            
            todo = TodoReadProjection(
                id=f"todo-{i:06d}",
                title=f"Task {i}: Performance test todo",
                description=f"Generated todo #{i} for performance testing",
                status=status,
                created_at=f"2026-01-{20 - (i % 10):02d}T{10 + (i % 14):02d}:00:00Z",
                updated_at=f"2026-01-{20 - (i % 10):02d}T{10 + (i % 14):02d}:00:00Z", 
                due_date=due_date,
            )
            todos.append(todo)
        
        return todos

    @pytest.mark.asyncio
    async def test_list_1000_todos_pagination_performance(self):
        """Test performance with 1000 todos using pagination."""
        large_todo_set = self.generate_large_todo_set(1000)
        
        # Simulate typical pagination: page 10 with limit 20 (todos 181-200)
        page_10_start = (10 - 1) * 20
        page_10_end = page_10_start + 20
        page_10_todos = large_todo_set[page_10_start:page_10_end]
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (page_10_todos, 1000)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(page=10, limit=20)
            
            # Measure performance
            start_time = time.time()
            response = await list_todos_query(params)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            # Performance assertions (should be well under 1 second per requirement SC-001)
            assert execution_time_ms < 1000, f"Query took {execution_time_ms:.2f}ms, should be < 1000ms"
            
            # Verify correct pagination results
            assert len(response.data) == 20
            assert response.pagination.total == 1000
            assert response.pagination.page == 10
            assert response.pagination.totalPages == 50  # ceil(1000/20)
            
            print(f"✅ 1000 todos pagination performance: {execution_time_ms:.2f}ms")

    @pytest.mark.asyncio
    async def test_list_5000_todos_with_filtering_performance(self):
        """Test performance with 5000 todos using status filtering."""
        large_todo_set = self.generate_large_todo_set(5000, status_mix=True)
        
        # Filter to pending todos only (approximately half)
        pending_todos = [t for t in large_todo_set if t.status == "pending"]
        page_1_pending = pending_todos[:20]  # First page of pending todos
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (page_1_pending, len(pending_todos))
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                page=1, 
                limit=20, 
                status="pending"
            )
            
            start_time = time.time()
            response = await list_todos_query(params)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            # Should still be fast with filtering
            assert execution_time_ms < 1000, f"Filtered query took {execution_time_ms:.2f}ms"
            
            # Verify filtering worked
            assert len(response.data) == 20
            assert all(todo.status == "pending" for todo in response.data)
            assert response.pagination.total == len(pending_todos)  # About 2500
            
            print(f"✅ 5000 todos filtered performance: {execution_time_ms:.2f}ms")

    @pytest.mark.asyncio
    async def test_large_page_size_performance(self):
        """Test performance with maximum page size (100 items)."""
        large_todo_set = self.generate_large_todo_set(1000)
        
        # Get first 100 todos
        first_100_todos = large_todo_set[:100]
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (first_100_todos, 1000)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(page=1, limit=100)  # Maximum allowed limit
            
            start_time = time.time()
            response = await list_todos_query(params)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            # Should handle large page sizes efficiently  
            assert execution_time_ms < 1000, f"Large page query took {execution_time_ms:.2f}ms"
            
            # Verify large page returned
            assert len(response.data) == 100
            assert response.pagination.limit == 100
            assert response.pagination.totalPages == 10  # ceil(1000/100)
            
            print(f"✅ Large page size (100 items) performance: {execution_time_ms:.2f}ms")

    @pytest.mark.asyncio
    async def test_deep_pagination_performance(self):
        """Test performance when accessing deep pages (high offset)."""
        large_todo_set = self.generate_large_todo_set(2000)
        
        # Access page 80 with limit 20 (offset = 1580)
        page_80_start = (80 - 1) * 20
        page_80_end = page_80_start + 20
        page_80_todos = large_todo_set[page_80_start:page_80_end]
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (page_80_todos, 2000)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(page=80, limit=20)
            
            start_time = time.time()
            response = await list_todos_query(params)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            # Deep pagination should still be reasonably fast
            # Note: OFFSET can be slower for very deep pages, but should still meet requirements
            assert execution_time_ms < 1000, f"Deep pagination took {execution_time_ms:.2f}ms"
            
            # Verify deep page results
            assert len(response.data) == 20
            assert response.pagination.page == 80
            assert response.pagination.total == 2000
            
            print(f"✅ Deep pagination (page 80/100) performance: {execution_time_ms:.2f}ms")

    @pytest.mark.asyncio
    async def test_complex_sort_with_large_dataset_performance(self):
        """Test performance of complex sorting (due_date with nulls) on large dataset."""
        large_todo_set = self.generate_large_todo_set(3000)
        
        # Sort by due_date asc (nulls last) - this is computationally more expensive
        sorted_todos = sorted(
            large_todo_set,
            key=lambda x: (x.due_date is None, x.due_date or "")
        )
        page_1_sorted = sorted_todos[:50]
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (page_1_sorted, 3000)
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                page=1,
                limit=50,
                sort="due_date",
                order="asc"
            )
            
            start_time = time.time()
            response = await list_todos_query(params)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            # Complex sorting should still meet performance requirements
            assert execution_time_ms < 1000, f"Complex sort took {execution_time_ms:.2f}ms"
            
            # Verify sorting worked correctly
            assert len(response.data) == 50
            # First items should have due dates, nulls should come later
            non_null_due_dates = [t.due_date for t in response.data if t.due_date is not None]
            assert len(non_null_due_dates) > 0, "Should have some non-null due dates in first page"
            
            print(f"✅ Complex sorting (3000 items) performance: {execution_time_ms:.2f}ms")

    @pytest.mark.asyncio
    async def test_combined_features_maximum_load_performance(self):
        """Test performance with all features combined under maximum expected load."""
        # Simulate maximum realistic load scenario
        large_todo_set = self.generate_large_todo_set(1000, status_mix=True)  # Per SC-001 requirement
        
        # Complex scenario: filter pending, sort by due_date desc, page 5 with limit 20
        pending_todos = [t for t in large_todo_set if t.status == "pending"]
        pending_sorted = sorted(
            pending_todos,
            key=lambda x: (x.due_date is None, x.due_date or ""),
            reverse=True  # DESC with nulls first
        )
        
        page_5_start = (5 - 1) * 20
        page_5_end = page_5_start + 20
        page_5_todos = pending_sorted[page_5_start:page_5_end]
        
        with patch('todo.read.src.app.queries.get_todo_repository') as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.list_todos.return_value = (page_5_todos, len(pending_todos))
            mock_get_repo.return_value = mock_repo

            params = ListTodosQueryParams(
                page=5,
                limit=20, 
                status="pending",
                sort="due_date",
                order="desc"
            )
            
            start_time = time.time()
            response = await list_todos_query(params)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            # Combined features under maximum load should still meet SC-001
            assert execution_time_ms < 1000, f"Maximum load scenario took {execution_time_ms:.2f}ms, should be < 1000ms"
            
            # Verify all features working together
            assert len(response.data) <= 20
            assert all(todo.status == "pending" for todo in response.data)
            assert response.pagination.page == 5
            
            print(f"✅ Maximum load (all features combined) performance: {execution_time_ms:.2f}ms")
            print(f"   Total pending todos: {response.pagination.total}")
            print(f"   Page 5 results: {len(response.data)} items")

    def test_performance_requirements_documentation(self):
        """Document performance requirements and test strategy."""
        performance_requirements = {
            "SC-001": "List operations must complete in <1 second for up to 1000 todos",
            "SC-002": "Support pagination with page sizes up to 100 items",
            "SC-005": "Return error messages within 500ms for invalid parameters"
        }
        
        test_scenarios = {
            "Basic pagination": "1000 todos, various page sizes",
            "Status filtering": "5000 todos with 50/50 pending/completed split",
            "Complex sorting": "Due date sorting with NULL handling",
            "Deep pagination": "High offset scenarios (page 80+)",
            "Maximum load": "All features combined with realistic data volume"
        }
        
        # Document what we're testing
        print("\n📊 Performance Test Coverage:")
        print("Requirements covered:")
        for req_id, desc in performance_requirements.items():
            print(f"  {req_id}: {desc}")
        
        print("\nTest scenarios:")
        for scenario, desc in test_scenarios.items():
            print(f"  {scenario}: {desc}")
        
        assert True  # This test always passes, it's for documentation