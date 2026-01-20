<!--
Sync Impact Report:
Version change: N/A → 1.0.0 (initial constitution)
Modified principles: N/A (new constitution)
Added sections:
  - Purpose
  - General engineering principles
  - Code quality standards (Simplicity and design discipline, Serverless testability, Modularity and isolation)
  - Testing standards (Test types, Property-based testing, TDD, Coverage requirements, Integration testing)
  - User experience consistency
  - Performance and reliability principles
  - Forbidden practices
  - Enforcement
Removed sections: N/A
Templates requiring updates:
  - ✅ plan-template.md (Constitution Check section updated)
  - ✅ spec-template.md (aligned with testing requirements)
  - ✅ tasks-template.md (aligned with TDD and testing requirements)
Follow-up TODOs: None
-->

# Constitution

## 1. Purpose

This constitution defines the engineering quality standards for this repository.

It governs:
- how code is written,
- how it is tested,
- how behavior is validated,
- and how performance and user experience are protected.

All specifications, plans, tasks, and generated code must comply with this constitution.
If there is a conflict, the constitution prevails.

## 2. General engineering principles

The following principles are mandatory and non-negotiable:

- Simplicity over cleverness
- Correctness over speed
- Explicit over implicit
- Readability over abstraction
- Testability over convenience

Code must favor clarity and predictability over sophistication.

## 3. Code quality standards

### 3.1 Simplicity and design discipline

- Code must follow:
    - YAGNI (You Aren't Gonna Need It)
    - KISS (Keep It Simple, Stupid)
    - DRY (Don't Repeat Yourself)
- Over-engineering and speculative abstractions are forbidden.
- Design must be minimal, direct, and intent-revealing.
- If a solution feels "clever", it is likely wrong.

### 3.2 Serverless testability (AWS Lambda)

Because the system is implemented using AWS Lambda:

- All business logic must be independent of AWS runtime constructs.
- Lambda handlers must be thin adapters over pure, testable functions.
- Core logic must be executable and testable on a developer machine:
    - without AWS credentials,
    - without cloud dependencies,
    - without deployed infrastructure.

### 3.3 Modularity and isolation

- Side effects (I/O, network calls, persistence) must be isolated at the edges.
- Pure logic must be testable without mocks.
- Mocks are allowed only at integration boundaries.

## 4. Testing standards (mandatory)

### 4.1 Test types

All bounded contexts and components must include:

- Unit tests
- Integration tests

Both are mandatory.

### 4.2 Property-based testing (primary testing strategy)

- Property-based testing is the default testing approach.
- Tests must validate behavior across ranges of inputs, not fixed examples.
- Properties must express:
    - invariants,
    - boundaries,
    - monotonicity,
    - idempotency,
    - error conditions.

Example (conceptual):

"For any valid input in range X, invariant Y always holds."

### 4.3 Test-Driven Development (TDD)

- TDD is mandatory for all new functions and logic.
- Tests must be written before implementation.
- Refactoring must preserve existing tests.

### 4.4 Behaviour-Driven Development (BDD)

- BDD is mandatory for all new functions and logic.
- Features must be written before implementation.
- Refactoring must preserve existing tests.

### 4.5 Coverage requirements

- Code coverage must be measured.
- Branch coverage is required, not only line coverage.
- New code must not reduce overall coverage.
- Coverage targets are enforced at CI level.
- Coverage numbers are not a vanity metric — untested behavior is considered undefined behavior.

### 4.6 Integration testing

- Integration tests must validate:
    - component interaction,
    - boundary behavior,
    - failure modes.
- External dependencies may be mocked only when:
    - the real dependency is non-deterministic,
    - slow,
    - or unavailable in local testing.

Mocks must model behavior, not implementation.

## 5. User experience consistency

- APIs must behave consistently across endpoints and bounded contexts.
- Error responses must be:
    - predictable,
    - structured,
    - actionable.
- Similar actions must produce similar responses.
- Breaking changes require explicit versioning and migration paths.

## 6. Performance and reliability principles

- Performance characteristics must be intentional and observable.
- No unnecessary allocations, blocking calls, or excessive retries.
- Functions must be:
    - deterministic,
    - retry-safe,
    - idempotent where applicable.

Slow paths and failure modes must be tested explicitly.

## 7. Forbidden practices

The following are explicitly forbidden:
- Untested code
- Example-only testing without property coverage
- Business logic inside Lambda handlers
- Clever abstractions without proven need
- Speculative generalization
- Tight coupling to cloud SDKs in core logic
- Code that cannot be executed locally

## 8. Enforcement

- Any code, plan, or generated artifact that violates this constitution is invalid.
- Violations must be corrected before proceeding.
- When in doubt, choose the simpler, more testable solution.

## Governance

This constitution supersedes all other practices and guidelines. Amendments require:

- Documentation of the change rationale
- Version increment according to semantic versioning:
    - **MAJOR**: Backward incompatible governance/principle removals or redefinitions
    - **MINOR**: New principle/section added or materially expanded guidance
    - **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements
- Update of dependent templates and documentation
- Compliance review to ensure all existing code and plans align with changes

All PRs and reviews must verify compliance with this constitution. Complexity must be justified. When in doubt, choose the simpler, more testable solution.

**Version**: 1.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07