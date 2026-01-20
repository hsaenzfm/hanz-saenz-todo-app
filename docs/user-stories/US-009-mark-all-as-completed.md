# US-009: Mark All as Completed

**Priority**: P2
**Created**: 2025-01-20
**Status**: Draft

## User Story

As a user, I want to mark all my pending tasks as completed at once so that I can quickly update multiple todos without individual actions.

**Why this priority**: Bulk actions improve efficiency when managing many todos. This feature allows users to complete multiple tasks simultaneously, which is valuable for productivity. While not essential for MVP, it's a useful enhancement. This is a P2 priority.

**Independent Test**: This can be fully tested by sending a request (method to be determined) to mark all pending todos as completed. The system should update all user's pending todos and return confirmation. This delivers value by enabling efficient bulk task completion.

**Associated Endpoints**:
- The PRD mentions requirement FR-016 for "Mark All as Completed" but doesn't specify the endpoint. This may be implemented as:
  - `PATCH /todos/completed` - Mark all pending todos as completed
  - `PUT /todos/bulk-status` - Bulk status update

**Related Requirements**:
- FR-016: System shall support "Mark All as Completed" bulk action
- FR-008: Users shall be able to toggle the is_completed status
- FR-019: System shall track created_at and updated_at timestamps for every entity
- FR-014: System shall return standard HTTP status codes (200, 201, 400, 401, 404, 500)
- FR-020: API shall return consistent JSON error objects

## Clarifying Questions

1. What HTTP method and endpoint should be used for this bulk operation?
2. Should this operation only affect pending todos, or all todos regardless of status?
3. Should the operation return a count of how many todos were updated?
4. Should there be a way to undo this operation?
5. Should this operation be idempotent (can be called multiple times safely)?
6. Should there be any confirmation or safety mechanism to prevent accidental bulk updates?
7. Should this operation respect filters (e.g., only mark todos matching certain criteria as completed)?
8. Should the API return the updated todos or just a summary/confirmation?

## Acceptance Scenarios (Given-When-Then)

### Happy Path

1. **Given** I am an authenticated user with multiple pending todos, **When** I send a request to mark all as completed, **Then** the system updates all pending todos to is_completed=true, updates their updated_at timestamps, and returns HTTP 200 with confirmation including count of updated todos

2. **Given** I am an authenticated user with only completed todos, **When** I send a request to mark all as completed, **Then** the system returns HTTP 200 with a count of 0 (no todos updated) since all are already completed

3. **Given** I am an authenticated user with a mix of completed and pending todos, **When** I send a request to mark all as completed, **Then** the system updates only the pending todos to completed and returns HTTP 200 with count of updated todos

### Error Scenarios

4. **Given** I am not authenticated, **When** I send a request to mark all as completed, **Then** the system returns HTTP 401 Unauthorized

5. **Given** the system encounters an unexpected error during bulk update, **When** a request to mark all as completed is processed, **Then** the system returns HTTP 500 with a consistent JSON error object

### Edge Cases

6. **Given** I am an authenticated user with zero todos, **When** I send a request to mark all as completed, **Then** the system returns HTTP 200 with a count of 0 (idempotent operation)

7. **Given** I am an authenticated user, **When** I send multiple requests to mark all as completed in quick succession, **Then** the system handles it idempotently - subsequent requests update 0 todos and return appropriate response

8. **Given** I am an authenticated user with a very large number of pending todos (e.g., 10,000), **When** I send a request to mark all as completed, **Then** the system processes all updates successfully or returns appropriate error if operation timeout/limit is exceeded

9. **Given** I am an authenticated user with todos, **When** I send a request to mark all as completed and some todos are being updated concurrently, **Then** the system handles the bulk operation correctly without conflicts

## Acceptance Criteria

### Functional Requirements

- AC-001: System MUST support marking all pending todos as completed in a single bulk operation
- AC-002: System MUST only affect pending todos (is_completed=false), leaving already completed todos unchanged
- AC-003: System MUST update the updated_at timestamp for each todo that is modified
- AC-004: System MUST ensure users can only update their own todos
- AC-005: Operation MUST be idempotent (safe to call multiple times)
- AC-006: System MUST return a count or summary of how many todos were updated

### API Requirements

- AC-007: API MUST return HTTP 200 (OK) status code on successful bulk update
- AC-008: API response SHOULD include count of updated todos and/or summary information
- AC-009: API MUST return HTTP 401 (Unauthorized) when authentication is required but not provided
- AC-010: API MUST return HTTP 500 (Internal Server Error) for unexpected system errors with consistent JSON error format
- AC-011: Response MUST be in consistent JSON format

### Validation Requirements

- AC-012: System MUST validate user authentication before processing bulk update
- AC-013: System MUST ensure atomicity or transaction integrity for the bulk operation

## Edge Cases

- What happens if the bulk operation partially fails (some todos updated, others failed)?
- Should there be a way to limit the bulk operation to a specific subset (e.g., only todos matching certain criteria)?
- How does the system handle concurrent individual todo updates during a bulk operation?
- Should there be a maximum limit on how many todos can be updated in a single bulk operation?
- What happens if a todo is deleted during the bulk update operation?
- Should the API provide detailed information about which todos were updated (IDs list)?
- How does the system handle performance with very large numbers of todos in bulk operations?
- Should there be an audit log for bulk operations to track when all todos were marked complete?