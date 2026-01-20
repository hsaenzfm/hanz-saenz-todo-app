# Implementation Plan: List Todos

**Branch**: `001-list-todos` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-list-todos/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements the ability to list todos with pagination, filtering by status, and sorting by creation date or due date. The implementation follows the CQRS pattern with read-side query handling that supports efficient querying of todo projections. The read handler will query the read-side PostgreSQL database with appropriate SQL filtering, sorting, and pagination logic.

## Technical Context

**Language/Version**: Python 3.11+ (AWS Lambda runtime)  
**Primary Dependencies**: psycopg (PostgreSQL driver), Powertools for AWS Lambda (Python), pytest (testing), hypothesis (property-based testing)  
**Storage**: Aurora RDS PostgreSQL (authoritative datastore for write side, read models for read side)  
**Testing**: pytest, hypothesis (property-based testing), local PostgreSQL containers for integration tests  
**Target Platform**: AWS Lambda (serverless), Aurora PostgreSQL  
**Project Type**: Bounded Context (CQRS pattern with write/read separation)  
**Performance Goals**: 
- List operations: <1 second for lists containing up to 1000 todos (per SC-001)
- Handle pagination requests with page sizes up to 100 items per page (per SC-002)
- Return clear error messages within 500ms for invalid parameters (per SC-005)
**Constraints**: 
- All queries must be efficient and use proper indexes
- Lambda handlers must be thin adapters
- Business logic must be testable without AWS dependencies
- No ORMs (explicit SQL only)
- Pagination uses offset-based approach (page/limit)
**Scale/Scope**: 
- Single-user or user-agnostic service (no multi-tenancy)
- No authentication/authorization required (per base-plan)
- Reasonable data volumes (standard web service assumptions)
- Support for up to 1000 todos per user (performance target)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Code Quality Standards

- **Simplicity and design discipline**: ✅ PASS
  - Implementation uses explicit SQL queries (no ORM abstraction)
  - Direct query handling without speculative abstractions
  - Minimal, intent-revealing code structure

- **Serverless testability**: ✅ PASS
  - Query logic will be pure functions testable without AWS
  - Lambda handler will be thin adapter over pure query functions
  - Core logic testable on developer machine without AWS credentials

- **Modularity and isolation**: ✅ PASS
  - Database access isolated in `infra/repo.py`
  - Query handling in `app/queries.py` (pure logic)
  - Side effects (DB queries) at infrastructure edge

### ✅ Testing Standards

- **Test types**: ✅ PASS
  - Unit tests required for query handlers (property-based)
  - Integration tests required for end-to-end query flow

- **Property-based testing**: ✅ PASS
  - Query handlers will be tested with property-based tests
  - Properties: pagination boundaries, filter correctness, sort ordering invariants

- **TDD/BDD**: ✅ PASS
  - Tests written before implementation (mandatory)
  - BDD scenarios already defined in spec.md

- **Coverage requirements**: ✅ PASS
  - All query logic must have branch coverage
  - New code must not reduce overall coverage

- **Integration testing**: ✅ PASS
  - Integration tests will validate DB queries with real PostgreSQL
  - AWS dependencies mocked at Lambda entrypoint

### ✅ User Experience Consistency

- ✅ Consistent error response format (JSON error objects)
- ✅ Standard HTTP status codes (200, 400, 401, 500)
- ✅ Consistent pagination metadata structure

### ✅ Performance and Reliability

- ✅ Deterministic queries with proper indexes
- ✅ Efficient pagination using SQL LIMIT/OFFSET
- ✅ Idempotent read operations (no side effects)

### ✅ Forbidden Practices

- ❌ No business logic in Lambda handlers (query logic in app/queries.py)
- ❌ No ORMs (explicit SQL only)
- ❌ No untested code (property-based + integration tests required)
- ❌ No example-only testing (property coverage mandatory)

**Gate Status**: ✅ **PASS** - All constitution requirements satisfied. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-list-todos/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

The repository structure follows the CQRS bounded context pattern defined in the architecture plan:

```text
todo/                     # Bounded Context name (from spec)
  db/                     # Sqitch project
    deploy/               # Deployment scripts
    revert/               # Revert scripts
    verify/               # Verification scripts
  write/                  # todo-write deployment unit
    src/
      entrypoints/        # AWS glue only (thin)
        api.py            # API Gateway -> CommandEnvelope
      app/                # command routing + use-cases (orchestrates domain+infra)
        commands.py       # envelope parsing
        create_todo_command.py       # Contains the command logic to create a ToDo
        command_handler.py       # mapping: command_type -> command object
        results.py        # stable command result shapes (for idempotency)
      domain/             # pure logic: state transitions + invariants (no AWS/DB)
        model.py          # aggregates/entities + transitions
        events.py         # event constructors (in-memory)
      infra/              # side effects: DB, outbox publishing clients, ACLs
        db.py             # psycopg connection + tx helpers
        repo.py           # SQL persistence (authoritative)
        outbox.py         # outbox insert + publisher client wrapper
        adapters.py       # ACL entrypoints (optional)
    tests/                # Property-based tests and Unit Tests
      unit/
        test_domain_properties.py    # property-based
        test_command_handlers.py     # property-based + examples
      integration/
        test_write_db_e2e.py         # real Postgres (container/local), AWS mocks

  read/                   # todo-read deployment unit (THIS FEATURE)
    src/
      entrypoints/        # AWS glue only (thin)
        api.py           # API Gateway queries (GET /todos)
      app/               # query handlers + projection update orchestration
        queries.py       # query routing/handlers (list_todos_query.py)
        projections.py   # event -> projection updater dispatch
      infra/
        db.py            # psycopg read connection helpers
        repo.py          # explicit SQL reads for projections (list query methods)
    tests/
      unit/
        test_projection_properties.py  # idempotency, ordering, invariants
        test_query_handlers.py         # property-based query handler tests
      integration/
        test_read_db_e2e.py            # real Postgres, full query flow
```

**Structure Decision**: The CQRS bounded context structure is mandated by the architecture plan. This feature implements the read-side query handling in the `todo/read/` deployment unit. The structure enforces separation of concerns: query logic is pure and testable, infrastructure concerns (database queries) are isolated at the edges, and Lambda entrypoints are thin adapters.

## Complexity Tracking

> **No violations to justify** - All design choices align with constitution requirements.

## Phase Completion Status

### ✅ Phase 0: Outline & Research (COMPLETE)

**Output**: `research.md`

All technical clarifications resolved:
- ✅ PostgreSQL pagination best practices (offset-based with LIMIT/OFFSET)
- ✅ Indexing strategy for filtering and sorting (composite indexes)
- ✅ Query optimization patterns (parameterized queries, explicit SQL)
- ✅ Property-based testing patterns (Hypothesis for query handlers)
- ✅ Error handling and validation patterns (early validation, structured errors)
- ✅ NULL handling in sorting (PostgreSQL NULLS LAST/FIRST)

### ✅ Phase 1: Design & Contracts (COMPLETE)

**Output**: `data-model.md`, `contracts/openapi.todo-list.yaml`, `quickstart.md`

**Data Model** (`data-model.md`):
- ✅ TodoReadProjection entity definition
- ✅ PaginationMetadata value object
- ✅ Query parameters and validation rules
- ✅ Response model structure
- ✅ Database indexes specification

**API Contracts** (`contracts/openapi.todo-list.yaml`):
- ✅ OpenAPI 3.0.3 specification
- ✅ GET /todos endpoint with all query parameters
- ✅ Request/response schemas
- ✅ Error response schemas
- ✅ Example responses

**Quickstart** (`quickstart.md`):
- ✅ Feature overview
- ✅ Implementation location guide
- ✅ Key components breakdown
- ✅ Database schema requirements
- ✅ API endpoint documentation
- ✅ Test strategy
- ✅ Implementation steps

**Agent Context Update**:
- ⚠️ Manual step required: Run `.specify/scripts/bash/update-agent-context.sh cursor-agent` when bash is available
- This step updates `.cursor/rules/specify-rules.mdc` with technology stack information

---

## Next Steps

1. ✅ **Phase 0 & 1 Complete** - All design artifacts generated
2. **Proceed to Phase 2**: Run `/speckit.tasks` command to break plan into implementation tasks
3. **Optional**: Run agent context update script when bash is available

## Generated Artifacts

- ✅ `plan.md` - This implementation plan
- ✅ `research.md` - Technical research and decisions
- ✅ `data-model.md` - Data structures and database schema
- ✅ `contracts/openapi.todo-list.yaml` - API contract specification
- ✅ `quickstart.md` - Quick reference guide for implementation

**Branch**: `001-list-todos`  
**Plan Path**: `specs/001-list-todos/plan.md`  
**Status**: ✅ Ready for task breakdown (Phase 2)
