# US-011: Get Todo Statistics

**Priority**: P2
**Created**: 2025-01-20
**Status**: Draft

## User Story

As a user, I want to see statistics about my tasks (count of pending vs completed) so that I can get an overview of my productivity and task status at a glance.

**Why this priority**: Statistics provide valuable insights for users to understand their task completion patterns and overall productivity. While not essential for MVP, it enhances the user experience with useful metrics. This is a P2 priority.

**Independent Test**: This can be fully tested by sending a GET request to `/todos/stats`. The system should return counts of pending and completed todos. This delivers value by providing actionable insights about task management.

**Associated Endpoints**:
- `GET /todos/stats` - Get count of pending vs completed tasks

**Related Requirements**:
- FR-019: System shall track created_at and updated_at timestamps for every entity
- FR-014: System shall return standard HTTP status codes (200, 201, 400, 401, 404, 500)
- FR-020: API shall return consistent JSON error objects

## Clarifying Questions

1. What specific statistics should be included? Should it be limited to pending/completed counts or include more metrics?
2. Should statistics include total count, completion percentage, or other derived metrics?
3. Should statistics be calculated in real-time or cached for performance?
4. Should statistics include todos created/completed in specific time periods (today, this week, this month)?
5. Should statistics be filtered by any criteria (e.g., only todos with due dates)?
6. Should statistics include breakdown by priority (how many High/Medium/Low priority pending todos)?
7. Should soft-deleted todos be included or excluded from statistics?
8. Should there be any additional metrics like average completion time, overdue todos count, etc.?

## Acceptance Scenarios (Given-When-Then)

### Happy Path

1. **Given** I am an authenticated user with a mix of completed and pending todos, **When** I send a GET request to `/todos/stats`, **Then** the system returns HTTP 200 with statistics including count of pending todos and count of completed todos

2. **Given** I am an authenticated user with only pending todos, **When** I send a GET request to `/todos/stats`, **Then** the system returns HTTP 200 with statistics showing pending count > 0 and completed count = 0

3. **Given** I am an authenticated user with only completed todos, **When** I send a GET request to `/todos/stats`, **Then** the system returns HTTP 200 with statistics showing pending count = 0 and completed count > 0

4. **Given** I am an authenticated user with zero todos, **When** I send a GET request to `/todos/stats`, **Then** the system returns HTTP 200 with statistics showing both pending and completed counts as 0

### Error Scenarios

5. **Given** I am not authenticated, **When** I send a GET request to `/todos/stats`, **Then** the system returns HTTP 401 Unauthorized

6. **Given** the system encounters an unexpected error during statistics calculation, **When** a GET request to `/todos/stats` is processed, **Then** the system returns HTTP 500 with a consistent JSON error object

### Edge Cases

7. **Given** I am an authenticated user, **When** I send a GET request to `/todos/stats` immediately after creating a new todo, **Then** the system returns updated statistics reflecting the new todo

8. **Given** I am an authenticated user, **When** I send a GET request to `/todos/stats` immediately after marking todos as completed, **Then** the system returns updated statistics reflecting the status changes

9. **Given** I am an authenticated user with a very large number of todos (e.g., 100,000), **When** I send a GET request to `/todos/stats`, **Then** the system calculates and returns statistics efficiently (may require optimization or caching)

10. **Given** I am an authenticated user with soft-deleted todos, **When** I send a GET request to `/todos/stats`, **Then** the system excludes soft-deleted todos from statistics (or includes them based on policy)

## Acceptance Criteria

### Functional Requirements

- AC-001: System MUST provide statistics via GET `/todos/stats` endpoint
- AC-002: System MUST return count of pending todos (is_completed=false)
- AC-003: System MUST return count of completed todos (is_completed=true)
- AC-004: System MUST calculate statistics only for the authenticated user's todos
- AC-005: System MUST return statistics in real-time (reflect current state) or with acceptable staleness if cached
- AC-006: Statistics MUST be accurate and consistent with actual todo counts

### API Requirements

- AC-007: API MUST return HTTP 200 (OK) status code on successful statistics retrieval
- AC-008: API MUST return statistics in a consistent JSON format
- AC-009: API MUST return HTTP 401 (Unauthorized) when authentication is required but not provided
- AC-010: API MUST return HTTP 500 (Internal Server Error) for unexpected system errors with consistent JSON error format
- AC-011: Response structure SHOULD be: `{ "pending": 5, "completed": 3, "total": 8 }` or similar format

### Validation Requirements

- AC-012: System MUST validate user authentication before calculating statistics
- AC-013: Statistics MUST exclude soft-deleted todos (if soft-deletion is implemented) or match deletion strategy
- AC-014: Count values MUST be non-negative integers

## Edge Cases

- Should statistics include a breakdown by priority level (pending High, pending Medium, pending Low, etc.)?
- Should statistics include time-based metrics (todos completed today, this week, etc.)?
- How does the system handle statistics calculation performance with very large datasets?
- Should statistics be cached to improve performance, and if so, what's the cache invalidation strategy?
- Should statistics include additional metrics like completion percentage or trends over time?
- What happens if todos are being created/deleted/updated concurrently while statistics are being calculated?
- Should there be separate statistics for todos with due dates vs those without?
- Should statistics include overdue todos count (todos with due_date in the past that are not completed)?
- How does the API handle statistics when user has no todos at all?
- Should the response include metadata like when statistics were calculated or cache expiry time?