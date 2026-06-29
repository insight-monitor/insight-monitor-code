---
title: Current Architecture State
type: reference
domain: architecture
priority: critical
status: accepted
version: 2.0.0
updated: 2026-06-29
---

# Current Architecture State (as of 2026-06-29)

This document is an honest assessment of the current architecture **after** the Clean Architecture migration (ARCH-0, PR #75). The legacy `backend/pipeline/` directory has been fully removed; all logic migrated to use cases and services. It complements the aspirational documents in this directory by describing what actually exists.

## Actual Directory Structure

```
backend/
├── application/               # Application Layer (Clean Architecture)
│   └── use_cases/             # IngestEvent, BuildSessions, InferIntent, GetSession
├── domain/                    # Domain Layer
│   ├── entities/              # RawEvent, SessionContext, IntentRecord
│   └── ports/                 # IEventRepository, ISessionRepository, IIntentRepository
├── infrastructure/            # Infrastructure Layer
│   ├── db/
│   │   ├── sqlite/            # SQLite repos, Database class, Unit of Work
│   │   └── in_memory/         # InMemory repos (unit test isolation)
│   └── di.py                  # Composition Root (Dependency Injection)
├── routes/                    # Presentation Layer (FastAPI routers)
│   ├── events.py              # POST/GET /events, /events/batch, /events/session/{id}
│   ├── sessions.py            # GET /sessions, /sessions/{id}, /sessions/{id}/intent, POST /sessions/{id}/close
│   ├── health.py              # GET /health, POST /heartbeat
│   └── tickets.py             # Full CRUD /tickets, /tickets/{id}/comments
├── services/                  # External service adapters
│   ├── llm_service.py         # OpenAI / Gemini API client
│   ├── prompt_builder.py      # Builds LLM prompts (migrated from legacy pipeline)
│   └── intent_parser.py       # Parses LLM JSON responses (migrated from legacy pipeline)
├── config.py                  # Centralized settings (pydantic-settings)
├── main.py                    # FastAPI app entry point
├── tests/                     # Tests
│   ├── conftest.py            # Fixtures: InMemory repos, TestClient with DI overrides
│   ├── test_health.py         # GET /health (1 test)
│   └── test_unit_use_cases.py # Use Case unit tests (10 tests, pytest -m unit)
└── data/                      # SQLite database (gitignored)
```

## Achieved Improvements (ARCH-1 through ARCH-11)

| Task | Status | Key Change |
|------|--------|------------|
| **ARCH-1** | Done | Database is a plain injectable class; no `get_instance()` singleton |
| **ARCH-2** | Done | Repository port interfaces in `domain/ports/repositories.py` |
| **ARCH-3** | Done | Domain entities in `domain/entities/` — zero infra imports |
| **ARCH-4** | Done | Use cases in `application/use_cases/` with port-only dependencies |
| **ARCH-5** | Done | SQLite + InMemory repository implementations |
| **ARCH-6** | Done | DI Composition Root in `infrastructure/di.py` |
| **ARCH-7** | Done | Repository-level commits; future transactional boundaries via DB connection wrapper |
| **ARCH-8** | Done | Capture agent resilience: buffer, retry with backoff, graceful shutdown |
| **ARCH-9** | Done | TypeScript types auto-generated from Pydantic via `scripts/generate_types.py`; run `npm run generate:types` |
| **ARCH-10** | Done | This document, ADRs, and related docs updated |
| **ARCH-11** | Done | Unit tests with InMemory repos; `pytest -m unit` in < 2s |
| **ARCH-0** | Done (PR #75) | Legacy `backend/pipeline/` removed — all logic migrated to use cases and services |

## Remaining Technical Debt

1. **No ADR process**: Architecture decisions were made during PR #43 without formal ADR records. This is being addressed in this update.
2. **Inference pipeline v0.1**: The `InferIntentUseCase` and LLM service exist but haven't been battle-tested with real Gemini traffic.
3. **Test coverage**: Unit tests exist for use cases. Integration tests for SQLite and E2E tests need expansion.

## Target Architecture

The long-term target is a strict Clean Architecture where:

```
Routes → Use Cases (Application) → Ports (Domain)
                                         ↑
                              Infrastructure (implements ports)
```

Every new feature = new Use Case class. Pipeline modules have been fully absorbed into use cases + services.

## Key Metrics

| Metric | Current |
|--------|---------|
| Unit test speed | < 2 seconds |
| Integration test speed | ~30 seconds |
| Code coupling | Zero infra imports in domain/application |
| Capture agent resilience | Buffer 500 events, retry 1s→2s→4s |
| Documented ADRs | 5 (ADR-0001 through ADR-0005) |
