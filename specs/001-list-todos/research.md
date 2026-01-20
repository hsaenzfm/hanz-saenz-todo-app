# Research: List Todos Feature

**Feature**: List Todos with Pagination, Filtering, and Sorting  
**Date**: 2026-01-20  
**Phase**: 0 - Research & Clarification

## Research Questions

### 1. PostgreSQL Pagination Best Practices

**Decision**: Use offset-based pagination with SQL LIMIT/OFFSET for simplicity and compatibility with existing requirements.

**Rationale**: 
- Requirements specify offset-based pagination (page/limit parameters)
- Simple to implement and understand
- Works well for moderate data volumes (target: up to 1000 todos per user)
- PostgreSQL efficiently handles LIMIT/OFFSET with proper indexes

**Implementation Pattern**:
```sql
SELECT * FROM todo_read_projection 
WHERE deleted_at IS NULL 
  AND ($1::text IS NULL OR status = $1::text)
ORDER BY 
  CASE WHEN $2::text = 'due_date' AND $3::text = 'asc' THEN due_date END ASC NULLS LAST,
  CASE WHEN $2::text = 'due_date' AND $3::text = 'desc' THEN due_date END DESC NULLS FIRST,
  CASE WHEN $2::text = 'created_at' AND $3::text = 'asc' THEN created_at END ASC,
  CASE WHEN $2::text = 'created_at' AND $3::text = 'desc' THEN created_at END DESC,
  created_at DESC  -- default fallback
LIMIT $4 OFFSET $5;
```

**Alternatives Considered**:
- Cursor-based pagination: More complex, requires stable sort keys, not required for current scale
- Keyset pagination: Better performance for large datasets but adds complexity; not needed for <1000 items

**References**: 
- PostgreSQL LIMIT/OFFSET documentation
- Offset-based pagination is standard for small-to-medium datasets

---

### 2. Indexing Strategy for Filtering and Sorting

**Decision**: Create composite indexes on (status, created_at DESC) and (status, due_date ASC) to support efficient filtering and sorting.

**Rationale**:
- Status filtering is a common query pattern (P1 priority)
- Sorting by created_at and due_date are required query patterns
- Composite indexes allow PostgreSQL to satisfy filter + sort in a single index scan
- NULLS LAST/FIRST handling in indexes aligns with sort requirements for due_date

**Index Definitions**:
```sql
-- For status filter + created_at sort
CREATE INDEX idx_todo_status_created_at ON todo_read_projection(status, created_at DESC) WHERE deleted_at IS NULL;

-- For status filter + due_date sort
CREATE INDEX idx_todo_status_due_date ON todo_read_projection(status, due_date ASC NULLS LAST) WHERE deleted_at IS NULL;

-- Default sort (created_at DESC) without filter
CREATE INDEX idx_todo_created_at ON todo_read_projection(created_at DESC) WHERE deleted_at IS NULL;
```

**Query Performance**:
- Index-only scans possible when all columns needed are in the index
- Filter predicates (WHERE status = X) can use index efficiently
- Sort operations use index order (no additional sort step)

**Alternatives Considered**:
- Single-column indexes: Less efficient for combined filter+sort queries
- Covering indexes (include all columns): Overhead not justified for current scale

**References**:
- PostgreSQL index types and partial indexes
- Composite index ordering for filter+sort optimization

---

### 3. Query Optimization Patterns

**Decision**: Use parameterized queries with explicit SQL, leverage PostgreSQL query planner optimizations, and implement query result caching at application level if needed.

**Rationale**:
- Explicit SQL allows full control over query plans
- Parameterized queries prevent SQL injection and enable query plan caching
- PostgreSQL query planner optimizes LIMIT/OFFSET efficiently with proper indexes
- Application-level caching can be added later if needed (not premature optimization)

**Query Pattern**:
```python
# Separate count query for pagination metadata
count_query = """
  SELECT COUNT(*) FROM todo_read_projection 
  WHERE deleted_at IS NULL 
    AND ($1::text IS NULL OR status = $1::text)
"""

# Main data query with limit/offset
data_query = """
  SELECT id, title, description, status, created_at, updated_at, due_date
  FROM todo_read_projection 
  WHERE deleted_at IS NULL 
    AND ($1::text IS NULL OR status = $1::text)
  ORDER BY ...
  LIMIT $4 OFFSET $5
"""
```

**Performance Considerations**:
- Count query is O(n) but acceptable for <1000 items with indexes
- LIMIT prevents fetching full result set
- OFFSET performance degrades with large offsets, but acceptable for typical use (first few pages)

**Alternatives Considered**:
- Estimated counts: Less accurate, not worth the complexity for current scale
- Cursor-based pagination: Better for very large datasets but adds complexity

---

### 4. Property-Based Testing Patterns for Query Handlers

**Decision**: Use Hypothesis for property-based testing with strategies that generate valid query parameters and validate invariants across query combinations.

**Rationale**:
- Property-based testing validates behavior across ranges of inputs (constitution requirement)
- Hypothesis is standard Python library for property-based testing
- Properties can express invariants: pagination consistency, filter correctness, sort ordering

**Test Properties to Validate**:
1. **Pagination Invariant**: For any valid page/limit, total = sum of all pages' item counts
2. **Filter Invariant**: All returned items match the status filter (if provided)
3. **Sort Invariant**: Items are ordered correctly according to sort parameters
4. **Boundary Invariant**: Empty results for pages beyond available data
5. **Combination Invariant**: Filter + sort + pagination work correctly together

**Example Property**:
```python
@given(
    status=st.one_of(st.none(), st.just("pending"), st.just("completed")),
    sort_field=st.one_of(st.just("created_at"), st.just("due_date")),
    sort_order=st.one_of(st.just("asc"), st.just("desc")),
    page=st.integers(min_value=1, max_value=100),
    limit=st.integers(min_value=1, max_value=100)
)
def test_list_todos_pagination_invariant(status, sort_field, sort_order, page, limit):
    # Given: todos exist in database
    # When: query executed with parameters
    result = list_todos_query(status, sort_field, sort_order, page, limit)
    # Then: all invariants hold
    assert all(item.status == status for item in result.items if status is not None)
    assert is_sorted(result.items, sort_field, sort_order)
    assert len(result.items) <= limit
    assert result.pagination.page == page
    assert result.pagination.limit == limit
```

**Alternatives Considered**:
- Example-based testing only: Insufficient coverage, violates constitution
- Manual test case generation: Less comprehensive than property-based

**References**:
- Hypothesis documentation for strategies and composite properties
- Property-based testing patterns for database queries

---

### 5. Error Handling and Validation Patterns

**Decision**: Validate query parameters at the query handler level, return structured error responses consistent with API contract.

**Rationale**:
- Early validation prevents unnecessary database queries
- Consistent error format improves user experience (constitution requirement)
- Parameter validation is pure logic, easily testable

**Validation Rules**:
- `page`: integer >= 1
- `limit`: integer >= 1 and <= 100 (max per SC-002)
- `status`: one of ["pending", "completed"] or None
- `sort`: one of ["created_at", "due_date"] or None
- `order`: one of ["asc", "desc"] or None (required if sort provided)

**Error Response Format**:
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid parameter: limit must be between 1 and 100",
    "field": "limit"
  }
}
```

**Alternatives Considered**:
- Database-level validation: Less flexible, harder to test
- Framework-level validation: Would require framework dependency, violates explicit SQL principle

---

### 6. NULL Handling in Sorting

**Decision**: Use PostgreSQL NULLS LAST for ascending sort and NULLS FIRST for descending sort when sorting by due_date, placing todos without due dates at the end (asc) or beginning (desc).

**Rationale**:
- Requirement FR-013 specifies NULL handling behavior
- PostgreSQL NULLS LAST/FIRST provides explicit control
- Consistent with user expectations (todos without due dates are less time-sensitive)

**Implementation**:
```sql
ORDER BY 
  CASE WHEN sort_field = 'due_date' AND order = 'asc' 
    THEN due_date END ASC NULLS LAST,
  CASE WHEN sort_field = 'due_date' AND order = 'desc' 
    THEN due_date END DESC NULLS FIRST,
  ...
```

**Alternatives Considered**:
- Treat NULL as distant future/past: Complex and less intuitive
- Separate NULL todos: Requires multiple queries, less efficient

---

## Summary

All technical questions resolved. Key decisions:
1. ✅ Offset-based pagination (SQL LIMIT/OFFSET)
2. ✅ Composite indexes for filter+sort optimization
3. ✅ Explicit SQL queries with parameterization
4. ✅ Property-based testing with Hypothesis
5. ✅ Early parameter validation with structured errors
6. ✅ PostgreSQL NULLS LAST/FIRST for due_date sorting

No outstanding clarifications. Ready to proceed to Phase 1 (Design & Contracts).
