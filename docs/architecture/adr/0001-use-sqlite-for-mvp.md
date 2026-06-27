# ADR-0001: Use SQLite for MVP

## Status

Accepted

## Context

The MVP needs a database for persisting captured events, sessions, and intent records. Options included PostgreSQL (requires server), LanceDB (vector search), and SQLite (embedded).

## Decision

Use SQLite with WAL mode for the MVP. SQLite requires zero configuration, no server process, and no Docker container. For a single-user MVP where sessions number in the hundreds, SQLite is faster and simpler than a client-server database.

## Consequences

- **Positive**: Zero infrastructure dependencies; database is a single file; easy backup and portability
- **Positive**: Thread-safe with WAL mode; sufficient for single-user concurrent access
- **Negative**: Not suitable for multi-user or multi-instance deployment; must be replaced for enterprise scaling
- **Negative**: No native vector search; would need LanceDB or similar for semantic search post-MVP
