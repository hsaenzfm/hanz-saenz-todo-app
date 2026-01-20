## Technical Context

**Language/Version**: Python 3.11+ (AWS Lambda runtime)  
**Primary Dependencies**: psycopg (PostgreSQL driver), Powertools for AWS Lambda (Python), pytest (testing), hypothesis (property-based testing)  
**Storage**: Aurora RDS PostgreSQL (authoritative datastore for write side, read models for read side)  
**Testing**: pytest, hypothesis (property-based testing), local PostgreSQL containers for integration tests  
**Target Platform**: AWS Lambda (serverless), Aurora PostgreSQL  
**Project Type**: Bounded Context (CQRS pattern with write/read separation)  
**Performance Goals**: 
- Create/retrieve operations: <2 seconds (per SC-001)
- State change log retrieval: <1 second (per SC-005)
- Handle 100 concurrent operations without data loss (per SC-003)
**Constraints**: 
- All writes must be transactional
- Idempotent command handling (mandatory)
- Soft DELETE only
- No ORMs (explicit SQL only)
- Lambda handlers must be thin adapters
- Business logic must be testable without AWS dependencies
**Scale/Scope**: 
- Single-user or user-agnostic service (no multi-tenancy)
- No authentication/authorization required
- Reasonable data volumes (standard web service assumptions)

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
        create_todo_command.py       # Containe the command logic to create a ToDo
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

  read/                   # todo-read deployment unit
    src/
      entrypoints/        # AWS glue only (thin)
        api.py           # API Gateway queries
        consume_events.py # event consumer -> projection updates
      app/               # query handlers + projection update orchestration
        queries.py       # query routing/handlers
        projections.py   # event -> projection updater dispatch
      infra/
        db.py            # psycopg read connection helpers
        repo.py          # explicit SQL reads/writes for projections
    tests/
      unit/
        test_projection_properties.py  # idempotency, ordering, invariants
      integration/
        test_read_db_e2e.py
```

**Structure Decision**: The CQRS bounded context structure is mandated by the architecture plan. This separates write-side command handling (with domain logic, transactional persistence, and event emission) from read-side query serving (with denormalized projections built from events). The structure enforces separation of concerns: domain logic is pure and testable, infrastructure concerns are isolated at the edges, and Lambda entrypoints are thin adapters.