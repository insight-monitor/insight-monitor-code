---
title: Current Architecture State
type: reference
domain: architecture
priority: critical
status: accepted
version: 1.0.0
updated: 2026-06-25
---

# Current Architecture State (as of 2026-06-25)

This document is an honest assessment of the current architecture **after** the Clean Architecture migration (ARCH-0, PR #43). It complements the aspirational documents in this directory by describing what actually exists.

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
│   └── health.py              # GET /health
├── pipeline/                  # Legacy/transitional pipeline modules
│   ├── session_builder.py     # Groups events into sessions
│   ├── inference_pipeline.py  # Orchestrates LLM inference
│   ├── prompt_builder.py      # Builds Gemini prompts
│   └── intent_parser.py       # Parses LLM JSON responses
├── services/                  # External service adapters
│   └── llm_service.py         # Gemini API client
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
| **ARCH-7** | Done | Unit of Work transaction boundaries in `infrastructure/db/sqlite/unit_of_work.py` |
| **ARCH-8** | Done | Capture agent resilience: buffer, retry with backoff, graceful shutdown |
| **ARCH-9** | **Not started** | TypeScript type generation from Pydantic still manual |
| **ARCH-10** | Partial | This document and related updates address the gap |
| **ARCH-11** | Done | Unit tests with InMemory repos; `pytest -m unit` in < 2s |

## Remaining Technical Debt

1. **ARCH-9 (TypeScript sync)**: Frontend types are still manually copied from Pydantic models. No generation script in place.
2. **Legacy pipeline modules**: `backend/pipeline/` still exists as a transitional directory. Some logic duplicates what use cases do. Eventually the use cases should fully absorb pipeline responsibilities.
3. **No ADR process**: Architecture decisions were made during PR #43 without formal ADR records. This is being addressed in this update.
4. **Inference pipeline v0.1**: The `InferIntentUseCase` and LLM service exist but haven't been battle-tested with real Gemini traffic.
5. **Test coverage**: Only unit tests for use cases exist. Integration tests for SQLite and E2E tests are minimal.

## Target Architecture

The long-term target is a strict Clean Architecture where:

```
Routes → Use Cases (Application) → Ports (Domain)
                                         ↑
                              Infrastructure (implements ports)
```

Every new feature = new Use Case class. No modifications to existing pipeline modules.

## Key Metrics

| Metric | Current |
|--------|---------|
| Unit test speed | < 2 seconds |
| Integration test speed | ~30 seconds |
| Code coupling | Zero infra imports in domain/application |
| Capture agent resilience | Buffer 500 events, retry 1s→2s→4s |
| Documented ADRs | 0 (being addressed) |
