# US-008: Sort Todos

**Priority**: P2
**Created**: 2025-01-20
**Status**: Draft

## User Story

As a user, I want to sort my tasks by creation date or due date so that I can organize my todos in a way that makes sense for my workflow.

**Why this priority**: Sorting functionality helps users prioritize and organize their todos effectively. While not essential for MVP, it significantly improves task management capabilities. This is a P2 priority.

**Independent Test**: This can be fully tested by sending a GET request to `/todos?sort=created_at` or `/todos?sort=due_date`. The system should return todos sorted by the specified field. This delivers value by enabling organized todo viewing.

**Associated Endpoints**:
- `GET /todos` - List all todos with optional sort parameter

**Related Requirements**:
- FR-018: Users shall be able to sort tasks by created_at or due_date
- FR-011: List API shall support pagination (page, limit)
- FR-014: System shall return standard HTTP status codes (200, 201, 400, 401, 404, 500)
- FR-020: API shall return consistent JSON error objects

## Clarifying Questions

1. Should sorting be ascending (ASC) or descending (DESC) by default?
2. Should the API support specifying sort direction explicitly (sort=created_at:desc)?
3. What should be the default sort order if no sort parameter is provided?
4. Should sorting work with todos that have null due_date values? Where should they appear?
5. Can sorting be combined with filtering and pagination?
6. Should the API support multi-field sorting (e.g., sort by priority first, then by due_date)?
7. Should sorting be case-sensitive for any text fields (if sorting by title is added later)?
8. What happens when sorting by due_date and some todos don't have a due_date?

## Acceptance Scenarios (Given-When-Then)

### Happy Path

1. **Given** I am an authenticated user with multiple todos, **When** I send a GET request to `/todos?sort=created_at`, **Then** the system returns HTTP 200 with todos sorted by created_at timestamp (ascending or descending per default)

2. **Given** I am an authenticated user with multiple todos, **When** I send a GET request to `/todos?sort=due_date`, **Then** the system returns HTTP 200 with todos sorted by due_date

3. **Given** I am an authenticated user, **When** I send a GET request to `/todos?sort=created_at&page=1&limit=10`, **Then** the system returns HTTP 200 with paginated results sorted by created_at

4. **Given** I am an authenticated user, **When** I send a GET request to `/todos?sort=created_at:desc`, **Then** the system returns HTTP 200 with todos sorted by created_at in descending order (newest first) if direction syntax is supported

### Error Scenarios

5. **Given** I am an authenticated user, **When** I send a GET request to `/todos?sort=invalid_field`, **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid sort field

6. **Given** I am an authenticated user, **When** I send a GET request to `/todos?sort=`, **Then** the system returns HTTP 400 with a consistent JSON error object indicating empty sort parameter OR ignores it (behavior to be specified)

7. **Given** I am not authenticated, **When** I send a GET request to `/todos?sort=created_at`, **Then** the system returns HTTP 401 Unauthorized

8. **Given** the system encounters an unexpected error during sorting, **When** a GET request to `/todos?sort=due_date` is processed, **Then** the system returns HTTP 500 with a consistent JSON error format

### Edge Cases

9. **Given** I am an authenticated user with todos where some have due_date and some don't, **When** I send a GET request to `/todos?sort=due_date`, **Then** the system returns todos with null due_dates either first or last (behavior to be specified) and todos with due_dates sorted appropriately

10. **Given** I am an authenticated user with todos having identical created_at timestamps, **When** I send a GET request to `/todos?sort=created_at`, **Then** the system returns todos in a consistent order (stable sort) - may use id as secondary sort

11. **Given** I am an authenticated user, **When** I send a GET request to `/todos?sort=due_date&status=pending`, **Then** the system returns filtered and sorted results correctly

12. **Given** I am an authenticated user with only one todo, **When** I send a GET request to `/todos?sort=created_at`, **Then** the system returns HTTP 200 with the single todo (sorting has no visible effect)

## Acceptance Criteria

### Functional Requirements

- AC-001: System MUST support sorting todos via sort query parameter on GET `/todos` endpoint
- AC-002: System MUST support sorting by "created_at" field
- AC-003: System MUST support sorting by "due_date" field
- AC-004: System MUST apply sorting before pagination (paginate sorted results)
- AC-005: System MUST ensure sorting only applies to authenticated user's todos
- AC-006: Sort parameter MUST be optional (can be omitted to use default sort order)
- AC-007: Sorting MUST maintain stable order for items with identical sort values

### API Requirements

- AC-008: API MUST return HTTP 200 (OK) status code on successful sorted retrieval
- AC-009: API MUST return sorted array of todo objects in the response body
- AC-010: API MUST maintain pagination metadata that reflects sorted results
- AC-011: API MUST return HTTP 400 (Bad Request) for invalid sort fields with consistent JSON error format
- AC-012: API MUST return HTTP 401 (Unauthorized) when authentication is required but not provided
- AC-013: API MUST return HTTP 500 (Internal Server Error) for unexpected system errors with consistent JSON error format

### Validation Requirements

- AC-014: Sort parameter MUST be one of: "created_at", "due_date" (and potentially direction suffix if supported)
- AC-015: Invalid sort field values MUST be rejected with HTTP 400
- AC-016: System MUST handle null due_date values appropriately during sorting (place at beginning or end)

## Edge Cases

- What happens when sorting by due_date and all todos have null due_date values?
- Should sorting work with search and filter parameters simultaneously?
- How does the system handle sorting performance with large datasets? Should there be database indexes?
- Should there be a way to sort by multiple fields (e.g., priority then due_date)?
- What happens when sort direction is specified in an invalid format?
- Should the API support reverse sorting without requiring a separate parameter?
- How does sorting interact with soft-deleted todos? Should they be excluded from sorted results?
- Should todos with identical sort values have a secondary sort key (e.g., by id or title) for consistency?