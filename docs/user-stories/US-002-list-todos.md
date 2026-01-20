# US-002: List Todos

**Priority**: P1
**Created**: 2025-01-20
**Status**: Draft

## User Story

As a user, I want to view all my tasks with support for pagination so that I can efficiently browse through my todo list and manage large numbers of tasks.

**Why this priority**: Listing todos is essential for users to see their existing tasks. Without this capability, users cannot view what they've created, making the system unusable. Pagination is critical for handling real-world scenarios where users may have many todos. This is a core MVP requirement.

**Independent Test**: This can be fully tested by sending a GET request to `/todos` with optional pagination parameters. The system should return a paginated list of todos. This delivers immediate value by allowing users to view their task list.

**Associated Endpoints**:
- `GET /todos` - List all todos (Paginated)

**Related Requirements**:
- FR-011: List API shall support pagination (page, limit)
- FR-019: System shall track created_at and updated_at timestamps for every entity
- FR-014: System shall return standard HTTP status codes (200, 201, 400, 401, 404, 500)
- FR-020: API shall return consistent JSON error objects

## Clarifying Questions

1. What should be the default page size (limit) if not specified? What should be the maximum allowed limit?
2. Should pagination use offset-based (page, limit) or cursor-based pagination?
3. Should the response include metadata about total count, total pages, current page, etc.?
4. What should be the default sorting order when not specified? Should it be by created_at descending (newest first)?
5. Should the API return all fields for each todo in the list, or a subset (summary view)?
6. What happens when requesting a page that doesn't exist (e.g., page 10 when there are only 5 pages)?
7. Should pagination parameters be query parameters (e.g., `?page=1&limit=20`) or headers?
8. How should the API handle invalid pagination parameters (negative page, zero limit, etc.)?

## Acceptance Scenarios (Given-When-Then)

### Happy Path

1. **Given** I am an authenticated user with multiple todos, **When** I send a GET request to `/todos` without pagination parameters, **Then** the system returns HTTP 200 with a paginated list of todos using default page size, and includes pagination metadata (current page, page size, total count, total pages)

2. **Given** I am an authenticated user, **When** I send a GET request to `/todos?page=1&limit=10`, **Then** the system returns HTTP 200 with up to 10 todos from page 1 and pagination metadata

3. **Given** I am an authenticated user with fewer todos than the page size, **When** I send a GET request to `/todos?page=1&limit=100`, **Then** the system returns HTTP 200 with all available todos and appropriate pagination metadata indicating total count

4. **Given** I am an authenticated user, **When** I send a GET request to `/todos?page=2&limit=5`, **Then** the system returns HTTP 200 with todos 6-10 (if they exist) and pagination metadata indicating page 2

### Error Scenarios

5. **Given** I am an authenticated user, **When** I send a GET request to `/todos?page=-1`, **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid page number

6. **Given** I am an authenticated user, **When** I send a GET request to `/todos?limit=0`, **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid limit

7. **Given** I am an authenticated user, **When** I send a GET request to `/todos?limit=10000` (exceeding maximum), **Then** the system returns HTTP 400 with a consistent JSON error object indicating limit exceeds maximum allowed

8. **Given** I am an authenticated user, **When** I send a GET request to `/todos?page=999` (non-existent page), **Then** the system returns HTTP 200 with an empty list and pagination metadata indicating no results

9. **Given** I am not authenticated, **When** I send a GET request to `/todos`, **Then** the system returns HTTP 401 Unauthorized

10. **Given** the system encounters an unexpected error during todo listing, **When** a GET request to `/todos` is processed, **Then** the system returns HTTP 500 with a consistent JSON error object

### Edge Cases

11. **Given** I am an authenticated user with zero todos, **When** I send a GET request to `/todos`, **Then** the system returns HTTP 200 with an empty list array and pagination metadata (total count: 0, total pages: 0 or 1)

12. **Given** I am an authenticated user, **When** I send a GET request to `/todos?page=abc` (invalid page format), **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid parameter type

13. **Given** I am an authenticated user, **When** I send a GET request to `/todos?limit=abc` (invalid limit format), **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid parameter type

14. **Given** I am an authenticated user with exactly one page of todos, **When** I send a GET request to `/todos?page=1&limit=10`, **Then** the system returns HTTP 200 with all todos and pagination metadata indicating page 1 of 1

## Acceptance Criteria

### Functional Requirements

- AC-001: System MUST support pagination using page and limit query parameters
- AC-002: System MUST return todos belonging to the authenticated user only
- AC-003: System MUST include pagination metadata in the response (at minimum: current page, page size, total count, total pages)
- AC-004: System MUST apply default page size if limit is not provided
- AC-005: System MUST apply default page (page 1) if page is not provided
- AC-006: System MUST return an empty list when requesting a valid page beyond available data
- AC-007: System MUST return all standard todo fields for each item in the list

### API Requirements

- AC-008: API MUST return HTTP 200 (OK) status code on successful retrieval
- AC-009: API MUST return a JSON response with an array of todo objects and pagination metadata
- AC-010: API MUST return HTTP 400 (Bad Request) for invalid pagination parameters with consistent JSON error format
- AC-011: API MUST return HTTP 401 (Unauthorized) when authentication is required but not provided
- AC-012: API MUST return HTTP 500 (Internal Server Error) for unexpected system errors with consistent JSON error format
- AC-013: Response structure MUST include: `{ "data": [...], "pagination": { "page": 1, "limit": 20, "total": 100, "totalPages": 5 } }`

### Validation Requirements

- AC-014: Page parameter MUST be a positive integer (>= 1)
- AC-015: Limit parameter MUST be a positive integer (>= 1)
- AC-016: Limit parameter MUST not exceed the maximum allowed value (to be specified)
- AC-017: Invalid parameter types (non-numeric) MUST be rejected with HTTP 400

## Edge Cases

- What happens when pagination parameters are provided as strings that can be parsed as integers (e.g., "1")?
- How does the system handle very large page numbers? Should there be a maximum page limit?
- What happens if the total count changes between pagination requests (todos added/deleted)?
- Should the API support cursor-based pagination as an alternative to offset-based?
- How does the system handle concurrent requests that might affect pagination results?
- What happens if a todo is deleted while a user is paginating through results?
- Should pagination metadata be optional or always included?
- How does the system handle database performance with large datasets? Should there be indexing requirements?