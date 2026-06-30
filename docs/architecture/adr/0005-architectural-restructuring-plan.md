# ADR-0005: Architectural Restructuring to Clean Architecture

## Status

Accepted

## Context

The prototype codebase had significant technical debt: singleton database, anemic domain models, transaction scripts in place of use cases, no dependency injection, and no unit test isolation. Before adding more features, the architecture needed to be restructured.

## Decision

Migrate from a prototype-grade structure (flat modules, singleton pattern, transaction scripts) to a Clean Architecture pattern with strict dependency inversion:

- **Domain Layer**: Entities and port interfaces (zero framework imports)
- **Application Layer**: Use cases depending only on ports
- **Infrastructure Layer**: SQLite repos, InMemory repos (for tests), DI composition root
- **Presentation Layer**: FastAPI routers using DI to receive use cases

The rule: inner layers never import from outer layers.

## Consequences

- **Positive**: Testable in isolation — unit tests use InMemory repos, zero disk/network, run in < 2s
- **Positive**: Dependency inversion — swapping SQLite for another database only requires a new repo implementation
- **Positive**: New features = new use case classes; no modification of existing pipeline code
- **Positive**: No singleton state shared between tests — zero shared state
- **Negative**: More boilerplate (port interfaces, DI wiring) compared to direct SQLite access
- **Negative**: Learning curve for developers unfamiliar with Clean Architecture
- **Negative**: Transitional duplication — legacy pipeline modules coexist with new use cases during migration
