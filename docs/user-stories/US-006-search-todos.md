# US-006: Search Todos

**Priority**: P2
**Created**: 2025-01-20
**Status**: Draft

## User Story

As a user, I want to search for tasks by keyword so that I can quickly find specific todos in my list without scrolling through all items.

**Why this priority**: Search functionality significantly improves usability when users have many todos. It allows quick access to specific tasks based on keywords. While not essential for MVP, it's valuable for user experience. This is a P2 priority.

**Independent Test**: This can be fully tested by sending a GET request to `/todos/search?q=keyword`. The system should return matching todos based on partial string matching on titles. This delivers value by enabling efficient todo discovery.

**Associated Endpoints**:
- `GET /todos/search` - Search tasks by keyword

**Related Requirements**:
- FR-013: Search functionality shall support partial string matching on titles
- FR-014: System shall return standard HTTP status codes (200, 201, 400, 401, 404, 500)
- FR-020: API shall return consistent JSON error objects

## Clarifying Questions

1. Should search be case-sensitive or case-insensitive?
2. Should search support searching in description fields in addition to titles?
3. Should search support multiple keywords or boolean operators (AND, OR)?
4. Should search results be paginated similar to list endpoint?
5. Should search support fuzzy matching or exact phrase matching?
6. What should be the maximum length of the search query?
7. Should search include completed todos or only pending ones?
8. Should search support special characters or escape sequences?

## Acceptance Scenarios (Given-When-Then)

### Happy Path

1. **Given** I am an authenticated user with todos titled "Buy groceries", "Buy milk", and "Call mom", **When** I send a GET request to `/todos/search?q=Buy`, **Then** the system returns HTTP 200 with todos matching "Buy groceries" and "Buy milk" (partial match)

2. **Given** I am an authenticated user with a todo titled "Finish PRD", **When** I send a GET request to `/todos/search?q=prd`, **Then** the system returns HTTP 200 with the "Finish PRD" todo (case-insensitive match, if implemented)

3. **Given** I am an authenticated user with a todo titled "Meeting with team", **When** I send a GET request to `/todos/search?q=team`, **Then** the system returns HTTP 200 with todos containing "team" in the title (partial string matching)

4. **Given** I am an authenticated user, **When** I send a GET request to `/todos/search?q=xyz` where no todos match, **Then** the system returns HTTP 200 with an empty array

### Error Scenarios

5. **Given** I am an authenticated user, **When** I send a GET request to `/todos/search` without a query parameter, **Then** the system returns HTTP 400 with a consistent JSON error object indicating query parameter is required

6. **Given** I am an authenticated user, **When** I send a GET request to `/todos/search?q=` (empty query), **Then** the system returns HTTP 400 with a consistent JSON error object indicating query cannot be empty OR returns HTTP 200 with empty results (behavior to be specified)

7. **Given** I am not authenticated, **When** I send a GET request to `/todos/search?q=test`, **Then** the system returns HTTP 401 Unauthorized

8. **Given** the system encounters an unexpected error during search, **When** a GET request to `/todos/search?q=test` is processed, **Then** the system returns HTTP 500 with a consistent JSON error object

### Edge Cases

9. **Given** I am an authenticated user, **When** I send a GET request to `/todos/search?q=verylongsearchquerythatmightexceedlimits`, **Then** the system either truncates the query, rejects it with HTTP 400, or processes it based on maximum length policy

10. **Given** I am an authenticated user with a todo titled "Special chars: @#$%", **When** I send a GET request to `/todos/search?q=@#$%`, **Then** the system handles special characters appropriately (escapes them or searches literally)

11. **Given** I am an authenticated user, **When** I send a GET request to `/todos/search?q=%20%20` (whitespace only), **Then** the system treats it as empty query and returns appropriate response

12. **Given** I am an authenticated user, **When** I send a GET request to `/todos/search?q=Buy&page=1&limit=10`, **Then** the system returns paginated search results if pagination is supported

## Acceptance Criteria

### Functional Requirements

- AC-001: System MUST support searching todos by keyword via GET `/todos/search?q=keyword` endpoint
- AC-002: System MUST support partial string matching on todo titles
- AC-003: System MUST return only todos belonging to the authenticated user
- AC-004: System MUST return todos where the search term appears anywhere in the title (not just at the beginning)
- AC-005: System SHOULD support pagination for search results (if implemented for list endpoint)
- AC-006: Search MUST be performed only on titles (not descriptions) per PRD requirement FR-013

### API Requirements

- AC-007: API MUST return HTTP 200 (OK) status code on successful search
- AC-008: API MUST return an array of matching todo objects in the response body
- AC-009: API MUST return HTTP 400 (Bad Request) for missing or invalid query parameter with consistent JSON error format
- AC-010: API MUST return HTTP 401 (Unauthorized) when authentication is required but not provided
- AC-011: API MUST return HTTP 500 (Internal Server Error) for unexpected system errors with consistent JSON error format
- AC-012: Response structure MUST be consistent with list endpoint format

### Validation Requirements

- AC-013: Query parameter (q) MUST be provided
- AC-014: Query parameter MUST not exceed maximum length (to be specified)
- AC-015: System MUST handle empty query string appropriately (reject or return empty results)

## Edge Cases

- What happens when search query contains SQL injection attempts or special database characters?
- How does the system handle search queries with unicode characters or emojis?
- Should search results be sorted by relevance, creation date, or another criteria?
- What happens when search returns a very large number of results? Should there be a limit?
- Should search include soft-deleted todos in results?
- How does the system handle search performance with large datasets? Should there be indexing requirements?
- Should search support wildcard characters (*, ?) for pattern matching?
- What happens when a user searches for a term that matches multiple todos across different pages?