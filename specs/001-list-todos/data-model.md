# Data Model: List Todos Feature

**Feature**: List Todos with Pagination, Filtering, and Sorting  
**Date**: 2026-01-20  
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data structures used by the list todos query feature. The read-side projection model is used for querying, while the write-side authoritative model (not shown here) is used for state changes.

## Read-Side Projection Model

### Entity: TodoReadProjection

The read-side projection of a todo, optimized for querying with pagination, filtering, and sorting.

**Table**: `todo_read_projection`

**Fields**:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | NOT NULL | Unique identifier for the todo (primary key) |
| `title` | VARCHAR(255) | NOT NULL | Todo title |
| `description` | TEXT | NULL | Optional description |
| `status` | VARCHAR(20) | NOT NULL | Completion status: 'pending' or 'completed' |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Last update timestamp |
| `due_date` | DATE | NULL | Optional due date |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | NULL | Soft delete timestamp (NULL = not deleted) |

**Constraints**:
- Primary key: `id`
- Check constraint: `status IN ('pending', 'completed')`
- Index: `idx_todo_created_at` on `(created_at DESC)` WHERE `deleted_at IS NULL`
- Index: `idx_todo_status_created_at` on `(status, created_at DESC)` WHERE `deleted_at IS NULL`
- Index: `idx_todo_status_due_date` on `(status, due_date ASC NULLS LAST)` WHERE `deleted_at IS NULL`

**Validation Rules**:
- `status` must be one of: 'pending', 'completed'
- `deleted_at IS NULL` for active todos (soft delete pattern)
- `due_date` can be NULL (todos without due dates)

**Query Behavior**:
- All queries exclude soft-deleted todos (`WHERE deleted_at IS NULL`)
- Sorting by `due_date` places NULLs at end (asc) or beginning (desc)

---

### Entity: PaginationMetadata

Metadata about pagination state for list query responses.

**Type**: Value object (not a database table)

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `page` | INTEGER | Current page number (1-based) |
| `limit` | INTEGER | Number of items per page |
| `total` | INTEGER | Total count of items matching filters |
| `totalPages` | INTEGER | Total number of pages (calculated: ceil(total / limit)) |

**Validation Rules**:
- `page >= 1`
- `limit >= 1` and `limit <= 100` (per SC-002)
- `total >= 0`
- `totalPages >= 0` (0 when total = 0)

**Calculations**:
- `totalPages = ceil(total / limit)` when `total > 0`, else `0`
- For empty results: `total = 0`, `totalPages = 0`, `page` remains as requested

---

## Query Parameters

### ListTodosQueryParams

Query parameters for the list todos endpoint.

**Type**: Value object

**Fields**:

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| `page` | INTEGER | No | 1 | Must be >= 1 |
| `limit` | INTEGER | No | 20 | Must be >= 1 and <= 100 |
| `status` | VARCHAR(20) | No | NULL | Must be 'pending' or 'completed' if provided |
| `sort` | VARCHAR(20) | No | 'created_at' | Must be 'created_at' or 'due_date' if provided |
| `order` | VARCHAR(10) | No | 'desc' | Must be 'asc' or 'desc' if provided |

**Default Behavior**:
- If `page` not provided: use `1`
- If `limit` not provided: use `20` (per assumptions)
- If `sort` not provided: use `'created_at'` (per FR-012)
- If `order` not provided: use `'desc'` (newest first, per FR-012)
- If `status` not provided: return all statuses

**Validation Rules**:
- `page`: positive integer >= 1
- `limit`: positive integer >= 1 and <= 100
- `status`: one of ['pending', 'completed'] or NULL
- `sort`: one of ['created_at', 'due_date'] or NULL (defaults to 'created_at')
- `order`: one of ['asc', 'desc'] or NULL (defaults to 'desc')
- If `sort` is provided, `order` can be provided (if not, uses default)

**Error Conditions**:
- Invalid `page`: HTTP 400 with error code `INVALID_PARAMETER`
- Invalid `limit`: HTTP 400 with error code `INVALID_PARAMETER`
- Invalid `status`: HTTP 400 with error code `INVALID_PARAMETER`
- Invalid `sort`: HTTP 400 with error code `INVALID_PARAMETER`
- Invalid `order`: HTTP 400 with error code `INVALID_PARAMETER`

---

## Query Response Model

### ListTodosResponse

Response structure for the list todos endpoint.

**Type**: Response object

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `data` | Array<TodoReadProjection> | Array of todo items (may be empty) |
| `pagination` | PaginationMetadata | Pagination metadata |

**Response Examples**:

**Success with data**:
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Complete project documentation",
      "description": "Write API documentation",
      "status": "pending",
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-20T10:00:00Z",
      "due_date": "2026-01-25"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "totalPages": 3
  }
}
```

**Success with empty results**:
```json
{
  "data": [],
  "pagination": {
    "page": 5,
    "limit": 20,
    "total": 45,
    "totalPages": 3
  }
}
```

---

## Relationships

- **TodoReadProjection** is a projection of the authoritative Todo aggregate from the write side
- Projections are maintained by event consumers that listen to Todo domain events
- No foreign key relationships (single-user/agnostic service, no multi-tenancy)

---

## State Transitions

Not applicable for read-side projections. State transitions occur in the write-side domain model (not part of this feature).

---

## Indexes

See indexes defined in the TodoReadProjection entity section above. Indexes support:
1. Default sort (created_at DESC)
2. Status filter + created_at sort
3. Status filter + due_date sort

All indexes are partial indexes (WHERE deleted_at IS NULL) to exclude soft-deleted todos.

---

## Data Integrity

- Projections are eventually consistent with the authoritative write model
- Read-side data may lag slightly behind writes (acceptable for query use case)
- Soft-deleted todos (`deleted_at IS NOT NULL`) are excluded from all queries
- No referential integrity constraints (single-entity queries)
