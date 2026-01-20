# US-003: Update Todo / Toggle Status

**Priority**: P1
**Created**: 2025-01-20
**Status**: Draft

## User Story

As a user, I want to edit task details or mark them as complete so that I can keep my todos up to date and track my progress.

**Why this priority**: Updating todos is essential functionality - users need to modify tasks as requirements change and mark them complete as work progresses. Without this, todos become static and lose their utility. This is a core MVP requirement.

**Independent Test**: This can be fully tested by sending a PUT request to `/todos/:id` to update todo fields or a PATCH request to `/todos/:id/status` to toggle completion. The system should update the todo and return the updated object. This delivers immediate value by allowing users to maintain accurate task information.

**Associated Endpoints**:
- `PUT /todos/:id` - Update an existing todo
- `PATCH /todos/:id/status` - Quickly toggle completion status

**Related Requirements**:
- FR-008: Users shall be able to toggle the is_completed status
- FR-010: Users shall be able to set a priority level (Low, Medium, High)
- FR-015: API shall validate input data before processing (e.g., title length)
- FR-018: Users shall be able to sort tasks by created_at or due_date
- FR-019: System shall track created_at and updated_at timestamps for every entity
- FR-014: System shall return standard HTTP status codes (200, 201, 400, 401, 404, 500)
- FR-020: API shall return consistent JSON error objects

## Clarifying Questions

1. Should PUT require all fields or allow partial updates? Should it replace the entire object or merge with existing?
2. Should PATCH /todos/:id/status only toggle, or should it accept a specific boolean value to set?
3. What happens if a user tries to update a todo that doesn't exist?
4. What happens if a user tries to update another user's todo?
5. Should updated_at be automatically updated by the server, or can the client provide it?
6. Can created_at be modified via update, or should it remain immutable?
7. Should the API support updating only specific fields (partial update) without requiring all fields?
8. What validation should occur when updating fields? Should it be the same as create validation?

## Acceptance Scenarios (Given-When-Then)

### Happy Path - Full Update (PUT)

1. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a PUT request to `/todos/123` with updated title, description, priority, and due_date, **Then** the system updates the todo with new values, automatically updates updated_at timestamp, and returns HTTP 200 with the updated todo object

2. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a PUT request to `/todos/123` with only title and description fields, **Then** the system updates those fields, preserves other existing fields (priority, due_date, is_completed), updates updated_at, and returns HTTP 200 with the updated todo

### Happy Path - Toggle Status (PATCH)

3. **Given** I am an authenticated user and I have a todo with id "123" that is not completed (is_completed=false), **When** I send a PATCH request to `/todos/123/status`, **Then** the system toggles is_completed to true, updates updated_at timestamp, and returns HTTP 200 with the updated todo

4. **Given** I am an authenticated user and I have a todo with id "123" that is completed (is_completed=true), **When** I send a PATCH request to `/todos/123/status`, **Then** the system toggles is_completed to false, updates updated_at timestamp, and returns HTTP 200 with the updated todo

### Error Scenarios

5. **Given** I am an authenticated user, **When** I send a PUT request to `/todos/999` (non-existent id), **Then** the system returns HTTP 404 with a consistent JSON error object indicating todo not found

6. **Given** I am an authenticated user, **When** I send a PATCH request to `/todos/999/status` (non-existent id), **Then** the system returns HTTP 404 with a consistent JSON error object indicating todo not found

7. **Given** I am an authenticated user, **When** I send a PUT request to `/todos/123` with an empty title, **Then** the system returns HTTP 400 with a consistent JSON error object indicating title cannot be empty

8. **Given** I am an authenticated user, **When** I send a PUT request to `/todos/123` with an invalid priority value, **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid priority

9. **Given** I am an authenticated user, **When** I send a PUT request to `/todos/123` with an invalid date format for due_date, **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid date format

10. **Given** I am not authenticated, **When** I send a PUT request to `/todos/123`, **Then** the system returns HTTP 401 Unauthorized

11. **Given** I am not authenticated, **When** I send a PATCH request to `/todos/123/status`, **Then** the system returns HTTP 401 Unauthorized

12. **Given** the system encounters an unexpected error during todo update, **When** a PUT request to `/todos/123` is processed, **Then** the system returns HTTP 500 with a consistent JSON error object

### Edge Cases

13. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a PUT request to `/todos/123` with the same values it already has, **Then** the system updates the updated_at timestamp and returns HTTP 200 with the todo (idempotent but timestamp changes)

14. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a PUT request to `/todos/123` attempting to change created_at, **Then** the system ignores the created_at change (keeps original) and updates other fields successfully

15. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a PUT request to `/todos/123` with title exceeding maximum length, **Then** the system returns HTTP 400 with validation error

16. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a PUT request to `/todos/123` with an invalid UUID format, **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid ID format

17. **Given** I am an authenticated user trying to update another user's todo, **When** I send a PUT request to `/todos/456` (belongs to different user), **Then** the system returns HTTP 403 (Forbidden) or HTTP 404 (to hide existence) with appropriate error message

## Acceptance Criteria

### Functional Requirements

- AC-001: System MUST allow updating todo fields via PUT `/todos/:id` endpoint
- AC-002: System MUST allow toggling is_completed status via PATCH `/todos/:id/status` endpoint
- AC-003: System MUST automatically update the updated_at timestamp when any field is modified
- AC-004: System MUST preserve created_at timestamp (make it immutable)
- AC-005: System MUST validate all updated fields using the same rules as creation
- AC-006: System MUST ensure users can only update their own todos
- AC-007: System MUST maintain data consistency during updates

### API Requirements

- AC-008: API MUST return HTTP 200 (OK) status code on successful update
- AC-009: API MUST return the updated todo object in the response body with all fields
- AC-010: API MUST return HTTP 400 (Bad Request) for validation errors with consistent JSON error format
- AC-011: API MUST return HTTP 401 (Unauthorized) when authentication is required but not provided
- AC-012: API MUST return HTTP 404 (Not Found) when todo does not exist or user doesn't have access
- AC-013: API MUST return HTTP 500 (Internal Server Error) for unexpected system errors with consistent JSON error format
- AC-014: PATCH `/todos/:id/status` MUST toggle the is_completed value (false → true, true → false)

### Validation Requirements

- AC-015: Title MUST be validated if provided (same rules as creation: required if provided, minimum length, maximum length)
- AC-016: Priority MUST be validated if provided (must be one of: Low, Medium, High)
- AC-017: Due_date MUST be validated if provided (valid ISO 8601 format)
- AC-018: Description MUST be validated if provided (maximum length if specified)
- AC-019: Todo ID MUST be a valid UUID format
- AC-020: Updated_at MUST be automatically set by server (cannot be set by client)

## Edge Cases

- What happens when updating a todo that was just deleted? Should it return 404 or allow update?
- How does the system handle concurrent updates to the same todo? Should there be optimistic locking?
- What happens if a user sends a PUT request with only some fields - should missing fields be set to null or preserved?
- Should the API support conditional updates (e.g., only update if current version matches)?
- How does the system handle updating todos that have relationships or dependencies (future consideration)?
- What happens when updating with fields that exceed database constraints?
- Should there be a rate limit on status toggle operations to prevent abuse?