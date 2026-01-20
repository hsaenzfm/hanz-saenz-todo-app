# Tasks: List Todos

**Input**: Design documents from `/specs/001-list-todos/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure with todo/read/src/ directory structure
- [x] T002 Initialize Python 3.11+ project with AWS Lambda dependencies in pyproject.toml
- [x] T003 [P] Configure pytest and hypothesis for testing in pyproject.toml
- [x] T004 [P] Setup PostgreSQL connection configuration in todo/read/src/infra/config.py
- [x] T005 [P] Setup AWS Lambda Powertools configuration in todo/read/src/infra/config.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create database schema for todo_read_projection table in todo/read/src/infra/schema.sql
- [x] T007 Setup database indexes for efficient querying in todo/read/src/infra/schema.sql
- [x] T008 [P] Implement base repository interface in todo/read/src/infra/repo.py
- [x] T009 [P] Create pagination metadata models in todo/read/src/domain/models.py
- [x] T010 [P] Setup error handling and validation in todo/read/src/domain/exceptions.py
- [x] T011 [P] Configure Lambda handler entrypoint structure in todo/read/src/entrypoints/api.py
- [x] T012 [P] Setup logging infrastructure using AWS Lambda Powertools in todo/read/src/infra/logging.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - List Todos with Pagination (Priority: P1) 🎯 MVP

**Goal**: Enable users to list their todos with pagination support for efficient browsing of task lists

**Independent Test**: Send GET request to `/todos` with optional pagination parameters. System returns paginated list of todos with metadata.

### Implementation for User Story 1

- [x] T013 [P] [US1] Create TodoReadProjection model in todo/read/src/domain/models.py
- [x] T014 [P] [US1] Create ListTodosResponse model with pagination metadata in todo/read/src/domain/models.py
- [x] T015 [P] [US1] Implement pagination validation logic in todo/read/src/domain/validation.py
- [x] T016 [US1] Implement list_todos_query handler in todo/read/src/app/queries.py
- [x] T017 [US1] Implement PostgreSQL repository methods for listing with pagination in todo/read/src/infra/repo.py
- [x] T018 [US1] Create Lambda API handler for GET /todos endpoint in todo/read/src/entrypoints/api.py
- [x] T019 [US1] Add parameter validation and error handling for pagination in todo/read/src/entrypoints/api.py
- [x] T020 [US1] Integration test for basic pagination functionality in tests/integration/test_list_todos.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Filter Todos by Status (Priority: P1)

**Goal**: Enable users to filter todos by completion status (pending/completed) to focus on specific task subsets

**Independent Test**: Send GET request to `/todos?status=pending` or `/todos?status=completed`. System returns only todos matching the specified status.

### Implementation for User Story 2

- [x] T021 [P] [US2] Add status filtering validation in todo/read/src/domain/validation.py
- [x] T022 [P] [US2] Create status filter enum in todo/read/src/domain/models.py
- [x] T023 [US2] Extend list_todos_query to handle status filtering in todo/read/src/app/queries.py
- [x] T024 [US2] Update repository methods to support status filtering in todo/read/src/infra/repo.py
- [x] T025 [US2] Update Lambda API handler to accept status parameter in todo/read/src/entrypoints/api.py
- [x] T026 [US2] Add status parameter validation in API layer in todo/read/src/entrypoints/api.py
- [x] T027 [US2] Integration test for status filtering functionality in tests/integration/test_list_todos_filter.py

**Checkpoint**: At this point, User Story 2 should be fully functional and testable independently

---

## Phase 5: User Story 3 - Sort Todos (Priority: P2)

**Goal**: Enable users to sort todos by creation date or due date to organize task lists according to priorities

**Independent Test**: Send GET request to `/todos?sort=created_at&order=asc` or `/todos?sort=due_date&order=desc`. System returns todos ordered according to specified criteria.

### Implementation for User Story 3

- [x] T028 [P] [US3] Add sort field and order validation in todo/read/src/domain/validation.py
- [x] T029 [P] [US3] Create sort criteria models in todo/read/src/domain/models.py
- [x] T030 [US3] Extend list_todos_query to handle sorting parameters in todo/read/src/app/queries.py
- [x] T031 [US3] Update repository methods to support dynamic sorting in todo/read/src/infra/repo.py
- [x] T032 [US3] Update Lambda API handler to accept sort and order parameters in todo/read/src/entrypoints/api.py
- [x] T033 [US3] Add sorting parameter validation in API layer in todo/read/src/entrypoints/api.py
- [x] T034 [US3] Integration test for sorting functionality in tests/integration/test_list_todos_sort.py

**Checkpoint**: At this point, User Story 3 should be fully functional and testable independently

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, optimization, and quality assurance

- [x] T035 [P] Add comprehensive error handling for database connection issues in todo/read/src/infra/repo.py
- [x] T036 [P] Add performance logging for query execution times in todo/read/src/app/queries.py
- [x] T037 [P] Implement request tracing with AWS X-Ray in todo/read/src/entrypoints/api.py
- [x] T038 End-to-end integration test combining all features in tests/integration/test_list_todos_complete.py
- [x] T039 Performance test for 1000+ todos pagination in tests/performance/test_list_performance.py
- [x] T040 [P] Add OpenAPI documentation generation in todo/read/src/entrypoints/openapi.py
- [x] T041 [P] Add deployment configuration for AWS Lambda in deploy/lambda-config.yaml

---

## Dependencies

### Story Completion Order
1. **User Story 1** (List with Pagination) - MVP baseline
2. **User Story 2** (Status Filtering) - Builds on US1, independent implementation
3. **User Story 3** (Sorting) - Builds on US1, independent implementation

### Critical Path
- Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) & Phase 5 (US3) can run in parallel → Phase 6

## Parallel Execution Examples

### User Story 1 (MVP)
- After T016: Can work in parallel on T017, T018, T019
- T013, T014, T015 can be done in parallel after Phase 2 completion

### User Stories 2 & 3 (After US1)
- US2 and US3 can be implemented completely in parallel
- Both extend the same base functionality without conflicts

## Implementation Strategy

**MVP Approach**: Implement User Story 1 first to establish a working baseline. This delivers immediate value and allows for early testing and feedback.

**Incremental Delivery**: Each user story builds upon the previous foundation but can be independently tested and deployed, enabling iterative improvement.

**Quality Gates**: Each phase includes integration tests to ensure the functionality works end-to-end before proceeding to the next increment.

## Summary

- **Total Tasks**: 41 tasks
- **User Story 1**: 8 tasks (MVP - List with Pagination)  
- **User Story 2**: 7 tasks (Status Filtering)
- **User Story 3**: 7 tasks (Sorting)
- **Infrastructure**: 12 tasks (Setup + Foundational)
- **Polish**: 7 tasks (Cross-cutting concerns)
- **Parallel Opportunities**: 19 tasks marked with [P] can run in parallel
- **MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 20 tasks