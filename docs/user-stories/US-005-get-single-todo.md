# US-005: Get Single Todo

**Priority**: P2
**Created**: 2025-01-20
**Status**: Draft

## User Story

As a user, I want to view the full details of a specific task so that I can review complete information about a particular todo item.

**Why this priority**: While listing todos provides an overview, viewing individual todo details is important for seeing complete information, especially for todos with long descriptions or complex metadata. However, it's not essential for MVP - users can manage with list view initially. This is a P2 priority.

**Independent Test**: This can be fully tested by sending a GET request to `/todos/:id` with a valid todo ID. The system should return the complete todo object with all fields. This delivers value by allowing users to access detailed todo information.

**Associated Endpoints**:
- `GET /todos/:id` - Get details of a single todo

**Related Requirements**:
- FR-019: System shall track created_at and updated_at timestamps for every entity
- FR-014: System shall return standard HTTP status codes (200, 201, 400, 401, 404, 500)
- FR-020: API shall return consistent JSON error objects

## Clarifying Questions

1. Should the API return all fields or allow field selection (sparse fieldsets)?
2. Should the API include additional computed fields or relationships in the response?
3. What happens if a user tries to access a todo that doesn't exist?
4. What happens if a user tries to access another user's todo?
5. Should soft-deleted todos be accessible via this endpoint?
6. Should the API support conditional requests (If-Modified-Since, ETags) for caching?
7. Should there be any rate limiting on individual todo retrieval?
8. Should the response include related data (e.g., if todos have tags, categories in future)?

## Acceptance Scenarios (Given-When-Then)

### Happy Path

1. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a GET request to `/todos/123`, **Then** the system returns HTTP 200 with the complete todo object including all fields: id, user_id, title, description, is_completed, priority, due_date, created_at, updated_at

2. **Given** I am an authenticated user and I have a todo with id "123" that has all optional fields populated, **When** I send a GET request to `/todos/123`, **Then** the system returns HTTP 200 with the complete todo object including all fields with their values

3. **Given** I am an authenticated user and I have a todo with id "123" that has minimal fields (only required ones), **When** I send a GET request to `/todos/123`, **Then** the system returns HTTP 200 with the todo object, with optional fields as null or omitted

### Error Scenarios

4. **Given** I am an authenticated user, **When** I send a GET request to `/todos/999` (non-existent id), **Then** the system returns HTTP 404 with a consistent JSON error object indicating todo not found

5. **Given** I am an authenticated user, **When** I send a GET request to `/todos/invalid-uuid` (invalid ID format), **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid ID format

6. **Given** I am not authenticated, **When** I send a GET request to `/todos/123`, **Then** the system returns HTTP 401 Unauthorized

7. **Given** I am an authenticated user trying to access another user's todo, **When** I send a GET request to `/todos/456` (belongs to different user), **Then** the system returns HTTP 403 (Forbidden) or HTTP 404 (to hide existence) with appropriate error message

8. **Given** the system encounters an unexpected error during todo retrieval, **When** a GET request to `/todos/123` is processed, **Then** the system returns HTTP 500 with a consistent JSON error object

### Edge Cases

9. **Given** I am an authenticated user and I have a soft-deleted todo with id "123", **When** I send a GET request to `/todos/123`, **Then** the system returns HTTP 404 (if soft-deleted todos are treated as not found) or includes a deleted flag in response (if they're still accessible)

10. **Given** I am an authenticated user, **When** I send a GET request to `/todos/123` immediately after creating it, **Then** the system returns HTTP 200 with the newly created todo

11. **Given** I am an authenticated user, **When** I send a GET request to `/todos/123` with an empty or malformed ID in the URL, **Then** the system returns HTTP 400 with a consistent JSON error object

## Acceptance Criteria

### Functional Requirements

- AC-001: System MUST return a single todo by ID via GET `/todos/:id` endpoint
- AC-002: System MUST return all standard todo fields in the response
- AC-003: System MUST ensure users can only access their own todos
- AC-004: System MUST return the most current version of the todo (not cached stale data)
- AC-005: System MUST exclude soft-deleted todos from retrieval (if soft-deletion is implemented)

### API Requirements

- AC-006: API MUST return HTTP 200 (OK) status code on successful retrieval
- AC-007: API MUST return the complete todo object in the response body with all fields
- AC-008: API MUST return HTTP 400 (Bad Request) for invalid ID format with consistent JSON error format
- AC-009: API MUST return HTTP 401 (Unauthorized) when authentication is required but not provided
- AC-010: API MUST return HTTP 404 (Not Found) when todo does not exist or user doesn't have access
- AC-011: API MUST return HTTP 500 (Internal Server Error) for unexpected system errors with consistent JSON error format
- AC-012: Response MUST include all entity fields: id, user_id, title, description, is_completed, priority, due_date, created_at, updated_at

### Validation Requirements

- AC-013: Todo ID MUST be a valid UUID format
- AC-014: System MUST validate that the todo exists and belongs to the authenticated user before returning it

## Edge Cases

- What happens if a todo is deleted while a GET request is in progress?
- How does the system handle concurrent GET requests for the same todo?
- Should the API support field filtering (only return specific fields to reduce payload size)?
- What happens if the todo data is corrupted or partially available?
- Should there be caching headers (ETag, Last-Modified) to support client-side caching?
- How does the system handle very large description fields in the response?
- Should the API include metadata about the todo (e.g., version number, last accessed time)?
- What happens if a todo was recently updated - should there be a way to indicate freshness?