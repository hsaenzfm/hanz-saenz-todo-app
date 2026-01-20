# Quickstart: List Todos Feature

**Feature**: List Todos with Pagination, Filtering, and Sorting  
**Date**: 2026-01-20

## Overview

This quickstart guide provides a concise overview of implementing the list todos feature. For detailed specifications, see [spec.md](./spec.md). For implementation details, see [plan.md](./plan.md).

## Feature Summary

Implement a read-side query handler that retrieves todos with support for:
- **Pagination**: Page-based navigation (page, limit parameters)
- **Filtering**: Filter by completion status (pending, completed)
- **Sorting**: Sort by creation date or due date (ascending/descending)

## Implementation Location

**Read-side handler**: `todo/read/src/app/queries.py`
- Function: `list_todos_query(status, sort, order, page, limit)`
- Repository: `todo/read/src/infra/repo.py`
- Entrypoint: `todo/read/src/entrypoints/api.py` (Lambda handler)

## Key Components

### 1. Query Handler (`app/queries.py`)

Pure function that orchestrates the query:
- Validates parameters
- Calls repository to fetch data
- Constructs response with pagination metadata

```python
def list_todos_query(
    status: Optional[str],
    sort: Optional[str],
    order: Optional[str],
    page: int,
    limit: int
) -> ListTodosResponse:
    # Parameter validation
    # Repository query
    # Response construction
```

### 2. Repository (`infra/repo.py`)

Database access layer with explicit SQL:
- Query todos with filters, sorting, pagination
- Count total matching items for pagination metadata
- Uses parameterized queries for safety

### 3. Lambda Handler (`entrypoints/api.py`)

Thin adapter that:
- Extracts query parameters from API Gateway event
- Calls query handler
- Formats HTTP response

## Database Schema

**Table**: `todo_read_projection`

Required fields for this feature:
- `id` (UUID)
- `title` (VARCHAR)
- `description` (TEXT, nullable)
- `status` (VARCHAR: 'pending' or 'completed')
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `due_date` (DATE, nullable)
- `deleted_at` (TIMESTAMP, nullable) - soft delete flag

**Indexes** (required for performance):
- `(created_at DESC)` WHERE `deleted_at IS NULL`
- `(status, created_at DESC)` WHERE `deleted_at IS NULL`
- `(status, due_date ASC NULLS LAST)` WHERE `deleted_at IS NULL`

## API Endpoint

**GET** `/todos`

**Query Parameters**:
- `page` (optional, default: 1): Page number (>= 1)
- `limit` (optional, default: 20): Items per page (1-100)
- `status` (optional): Filter by 'pending' or 'completed'
- `sort` (optional, default: 'created_at'): Sort field ('created_at' or 'due_date')
- `order` (optional, default: 'desc'): Sort direction ('asc' or 'desc')

**Response**:
```json
{
  "data": [/* array of todo objects */],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "totalPages": 3
  }
}
```

See [contracts/openapi.todo-list.yaml](./contracts/openapi.todo-list.yaml) for full API contract.

## Test Strategy

### Unit Tests (`tests/unit/test_query_handlers.py`)

Property-based tests using Hypothesis:
- Pagination invariants (all pages sum to total)
- Filter correctness (all items match status filter)
- Sort ordering correctness
- Boundary conditions (empty results, large page numbers)

### Integration Tests (`tests/integration/test_read_db_e2e.py`)

End-to-end tests with real PostgreSQL:
- Full query flow from Lambda handler to database
- Parameter validation and error handling
- Pagination, filtering, sorting combinations

## Implementation Steps

1. **Create database indexes** (Sqitch migration)
   - Partial indexes for filtering and sorting
   - See [research.md](./research.md) for index definitions

2. **Implement repository methods** (`infra/repo.py`)
   - `list_todos(..., page, limit)` - data query
   - `count_todos(...)` - count query for pagination

3. **Implement query handler** (`app/queries.py`)
   - Parameter validation
   - Repository calls
   - Response construction

4. **Implement Lambda handler** (`entrypoints/api.py`)
   - Parameter extraction from API Gateway event
   - Query handler invocation
   - HTTP response formatting

5. **Write property-based tests**
   - Test query handler with Hypothesis
   - Validate invariants and edge cases

6. **Write integration tests**
   - Test full flow with real database
   - Validate API contract compliance

## Key Constraints

- ✅ No ORMs - explicit SQL only
- ✅ Lambda handler must be thin (business logic in app/queries.py)
- ✅ All logic must be testable without AWS dependencies
- ✅ Property-based testing is mandatory (constitution requirement)
- ✅ Soft-deleted todos excluded from all queries (`deleted_at IS NULL`)

## Performance Targets

- ✅ List operations: <1 second for up to 1000 todos (SC-001)
- ✅ Page sizes up to 100 items (SC-002)
- ✅ Error responses: <500ms (SC-005)

## Next Steps

1. Review [spec.md](./spec.md) for detailed requirements
2. Review [plan.md](./plan.md) for implementation approach
3. Review [research.md](./research.md) for technical decisions
4. Review [data-model.md](./data-model.md) for data structures
5. Review [contracts/openapi.todo-list.yaml](./contracts/openapi.todo-list.yaml) for API contract
6. Proceed to task breakdown ([tasks.md](./tasks.md) - created by `/speckit.tasks` command)
