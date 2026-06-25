---
title: Architecture — Clean Architecture MVP & Enterprise DER
type: conceptual
domain: architecture
priority: high
status: accepted
version: 2.0.0
updated: 2026-06-25
---

# Insight Monitor — Architecture Overview

This document reflects the **actual current state** of the codebase after the Clean Architecture migration (ARCH-0, Issue #41) and defines the boundaries toward the future Enterprise cloud architecture.

---

## Current State: Clean Architecture (MVP — Post ARCH-0)

The backend has been fully migrated from a prototype-grade structure to a **Clean Architecture** pattern. The key rule is: **inner layers never depend on outer layers**.

```
┌─────────────────────────────────────────────────────┐
│                   Presentation Layer                 │
│         backend/routes/  (FastAPI routers)           │
├─────────────────────────────────────────────────────┤
│                  Application Layer                   │
│        backend/application/use_cases/               │
│  IngestEvent · BuildSessions · InferIntent · Get    │
├─────────────────────────────────────────────────────┤
│                    Domain Layer                      │
│   backend/domain/entities/   (RawEvent, Session…)   │
│   backend/domain/ports/      (IEventRepo, etc.)     │
├─────────────────────────────────────────────────────┤
│                Infrastructure Layer                  │
│   backend/infrastructure/db/sqlite/   (SQLite)       │
│   backend/infrastructure/db/in_memory/ (Tests)       │
│   backend/infrastructure/di.py   (Composition Root) │
└─────────────────────────────────────────────────────┘
```

### Dependency Rule
- **Routes** only call **Use Cases** (via FastAPI `Depends`)
- **Use Cases** only depend on **Ports** (ABCs in `domain/ports/`)
- **Ports** know nothing about SQLite, HTTP, or any framework
- **Infrastructure** implements Ports; never imported by Domain or Application

---

## Completed ARCH Tasks (ARCH-0 / Issue #41)

| Task | Description | Location |
|------|-------------|----------|
| **ARCH-1** | Remove DB Singleton | `infrastructure/db/sqlite/database.py` |
| **ARCH-2** | Repository Ports (Interfaces) | `domain/ports/repositories.py` |
| **ARCH-3** | Domain Layer (Entities) | `domain/entities/` |
| **ARCH-4** | Application Layer (Use Cases) | `application/use_cases/` |
| **ARCH-5** | Infrastructure Repositories | `infrastructure/db/sqlite/` + `infrastructure/db/in_memory/` |
| **ARCH-6** | DI Composition Root | `infrastructure/di.py` |
| **ARCH-7** | Transaction Boundaries (Unit of Work) | `infrastructure/db/sqlite/unit_of_work.py` |
| **ARCH-8** | Capture Agent Resilience | `capture/event_sender.py` (buffer + retry) |
| **ARCH-10** | Architecture Docs updated | This document |
| **ARCH-11** | Unit Tests with Mocks | `tests/test_unit_use_cases.py` |

---

## Database Layer: SQLite MVP

**Engine:** Local SQLite (`data/insight_monitor.db`)
**Mode:** WAL (Write-Ahead Logging) for thread-safe concurrency
**Scope:** Single-user, local machine

### Tables

| Table | Purpose |
|-------|---------|
| `raw_events` | Captures every window focus, screenshot, and input activity event |
| `sessions` | Groups events into logical work sessions by time and inactivity |
| `intent_records` | Stores AI-inferred intent (goal, type, confidence) per session |

### Repository Pattern
Each table has a **Port (interface)** in `domain/ports/repositories.py` and a **concrete SQLite implementation** in `infrastructure/db/sqlite/repositories.py`. Tests use the **InMemory** implementations from `infrastructure/db/in_memory/repositories.py`.

---

## Capture Agent Resilience (ARCH-8)

The `capture/event_sender.py` now includes:
- **Local buffer** (up to 500 events) when the backend is unreachable
- **Exponential backoff** retries (1s → 2s → 4s)
- **Auto-flush** on reconnect: pending events are sent as soon as the API comes back online
- **Graceful shutdown**: flushes the buffer before closing

---

## Running Tests

```bash
# Unit tests only (< 2s, no disk, no network)
pytest -m unit

# Integration tests (uses SQLite on disk)
pytest -m integration

# All tests
pytest
```

---

## Phase 2: Cloud Enterprise (Target ERD)

The official ERD documents the **target cloud architecture** for a Multi-Tenant SaaS platform.

**Planned changes:**
- **Engine:** MySQL / PostgreSQL (centralized server)
- **Scope:** Multi-tenant (Companies → Users → Multiple Agents/Teams)
- **Sync Agent:** Local SQLite → Central MySQL via a background sync service

### Post-MVP Modules (not in current scope)
1. **Organizational Module**: `company`, `user`, `role`, `user_role`
2. **Agents Module**: Capture client registration per machine (`agent`)
3. **Privacy Module**: Redaction engine and censorship rules
4. **Reports & Audit Module**: Pre-computed analytical reports and access logs
5. **Strict Normalization**: Separation of `event`, `screenshot`, `ocr_text`, `active_window`

### Migration Strategy
Local UUID identifiers generated in SQLite will be preserved. A **Sync Agent** service will replicate them to the central MySQL cluster, injecting `user_id` and `agent_id` foreign keys resolved from the device's authentication token.

---

*For the exact SQLite schema, see [`database-schema.md`](./database-schema.md).*
*For the complete ERD diagram, see [`img/der-complete.png`](./img/der-complete.png).*
