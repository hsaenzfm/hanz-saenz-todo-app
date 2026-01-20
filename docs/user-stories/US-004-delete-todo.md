# US-004: Delete Todo

**Priority**: P2
**Created**: 2025-01-20
**Status**: Draft

## User Story

As a user, I want to remove tasks I no longer need so that I can keep my todo list clean and focused on active tasks.

**Why this priority**: While deletion is important for maintaining a clean todo list, it's not essential for the core MVP. Users can mark todos as complete instead. However, deletion provides better user experience for removing tasks that are no longer relevant. This is a P2 priority.

**Independent Test**: This can be fully tested by sending a DELETE request to `/todos/:id`. The system should delete the todo and return appropriate status. This delivers value by allowing users to remove irrelevant or incorrect todos.

**Associated Endpoints**:
- `DELETE /todos/:id` - Delete a specific todo

**Related Requirements**:
- FR-009: System shall support soft-deletion or hard-deletion of tasks
- FR-014: System shall return standard HTTP status codes (200, 201, 400, 401, 404, 500)
- FR-020: API shall return consistent JSON error objects

## Clarifying Questions

1. Should the system use soft-deletion (mark as deleted but keep in database) or hard-deletion (permanently remove)?
2. If soft-deletion is used, should there be a mechanism to restore deleted todos?
3. Should deleted todos still count toward user statistics or be excluded?
4. What happens if a user tries to delete a todo that doesn't exist?
5. What happens if a user tries to delete another user's todo?
6. Should there be confirmation or undo capability for deletion?
7. If soft-deletion is used, should the API provide endpoints to view or manage deleted todos?
8. Should there be a retention period for soft-deleted todos before permanent deletion?

## Acceptance Scenarios (Given-When-Then)

### Happy Path

1. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a DELETE request to `/todos/123`, **Then** the system deletes (soft or hard) the todo and returns HTTP 200 or HTTP 204 (No Content) indicating successful deletion

2. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a DELETE request to `/todos/123`, **Then** the todo is no longer accessible via GET `/todos/123` (returns 404) and is removed from list endpoints

### Error Scenarios

3. **Given** I am an authenticated user, **When** I send a DELETE request to `/todos/999` (non-existent id), **Then** the system returns HTTP 404 with a consistent JSON error object indicating todo not found

4. **Given** I am an authenticated user, **When** I send a DELETE request to `/todos/invalid-uuid` (invalid ID format), **Then** the system returns HTTP 400 with a consistent JSON error object indicating invalid ID format

5. **Given** I am not authenticated, **When** I send a DELETE request to `/todos/123`, **Then** the system returns HTTP 401 Unauthorized

6. **Given** I am an authenticated user trying to delete another user's todo, **When** I send a DELETE request to `/todos/456` (belongs to different user), **Then** the system returns HTTP 403 (Forbidden) or HTTP 404 (to hide existence) with appropriate error message

7. **Given** the system encounters an unexpected error during todo deletion, **When** a DELETE request to `/todos/123` is processed, **Then** the system returns HTTP 500 with a consistent JSON error object

### Edge Cases

8. **Given** I am an authenticated user, **When** I send multiple DELETE requests to `/todos/123` (idempotent operation), **Then** the system returns the same success status (200/204) on subsequent attempts (idempotent deletion)

9. **Given** I am an authenticated user and I have a todo with id "123", **When** I send a DELETE request to `/todos/123` and then immediately try to update it, **Then** the update request returns HTTP 404 indicating the todo no longer exists

10. **Given** I am an authenticated user, **When** I send a DELETE request to `/todos/123` with an already soft-deleted todo, **Then** the system either returns HTTP 404 (if treated as not found) or HTTP 200/204 (if allows repeated deletion)

## Acceptance Criteria

### Functional Requirements

- AC-001: System MUST support deletion of todos via DELETE `/todos/:id` endpoint
- AC-002: System MUST ensure users can only delete their own todos
- AC-003: System MUST implement either soft-deletion (mark as deleted) or hard-deletion (permanent removal)
- AC-004: System MUST remove deleted todos from list and get endpoints (if hard-deletion) or filter them out (if soft-deletion)
- AC-005: System MUST maintain referential integrity if soft-deletion is used (mark with deleted_at timestamp or is_deleted flag)
- AC-006: Deletion operation MUST be idempotent (multiple delete requests should not cause errors)

### API Requirements

- AC-007: API MUST return HTTP 200 (OK) or HTTP 204 (No Content) status code on successful deletion
- AC-008: API response body MAY be empty on successful deletion (204 No Content) or include confirmation message
- AC-009: API MUST return HTTP 400 (Bad Request) for invalid ID format with consistent JSON error format
- AC-010: API MUST return HTTP 401 (Unauthorized) when authentication is required but not provided
- AC-011: API MUST return HTTP 404 (Not Found) when todo does not exist or user doesn't have access
- AC-012: API MUST return HTTP 500 (Internal Server Error) for unexpected system errors with consistent JSON error format

### Validation Requirements

- AC-013: Todo ID MUST be a valid UUID format
- AC-014: System MUST validate that the todo exists and belongs to the authenticated user before deletion

## Edge Cases

- What happens if a todo is being updated at the same time as deletion? Should there be conflict handling?
- How does the system handle cascading deletions if todos have relationships (future consideration)?
- Should there be a confirmation step for deletion, or is it immediate?
- What happens to associated data (comments, attachments) when a todo is deleted?
- If soft-deletion is used, should there be automatic permanent deletion after a retention period?
- Should the API provide audit logs of deletions for compliance purposes?
- How does the system handle bulk deletion scenarios (if multiple todos are deleted simultaneously)?
- Should deleted todos be excluded from search results immediately after deletion?