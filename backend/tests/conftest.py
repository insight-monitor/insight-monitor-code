"""
ARCH-11: conftest.py refactorizado.
- `client` usa DI override de FastAPI con repos InMemory (cero disco, cero SQLite).
- `in_memory_repos` fixture provee repos limpios para tests unitarios de Use Cases.
"""

import pytest
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.infrastructure.db.in_memory.repositories import (
    InMemoryEventRepository,
    InMemorySessionRepository,
    InMemoryIntentRepository,
)
from backend.infrastructure.di import (
    get_event_repository,
    get_session_repository,
    get_intent_repository,
    get_ingest_event_use_case,
    get_get_session_use_case,
)


@asynccontextmanager
async def noop_lifespan(_app: FastAPI):
    yield


# ── Fixture: repos en memoria para tests unitarios de Use Cases ───────────────

@pytest.fixture()
def event_repo():
    return InMemoryEventRepository()


@pytest.fixture()
def session_repo():
    return InMemorySessionRepository()


@pytest.fixture()
def intent_repo():
    return InMemoryIntentRepository()


# ── Fixture: TestClient con FastAPI overrides (cero disco) ────────────────────

@pytest.fixture()
def client():
    """
    Cliente HTTP que usa repositorios InMemory inyectados via FastAPI Depends override.
    Cada test obtiene una app limpia — zero shared state.
    """
    mem_event = InMemoryEventRepository()
    mem_session = InMemorySessionRepository()
    mem_intent = InMemoryIntentRepository()

    from backend.main import app
    from backend.application.use_cases.ingest_event import IngestEventUseCase
    from backend.application.use_cases.get_session import GetSessionUseCase

    app.dependency_overrides[get_event_repository] = lambda: mem_event
    app.dependency_overrides[get_session_repository] = lambda: mem_session
    app.dependency_overrides[get_intent_repository] = lambda: mem_intent
    app.dependency_overrides[get_ingest_event_use_case] = lambda: IngestEventUseCase(mem_event)
    app.dependency_overrides[get_get_session_use_case] = lambda: GetSessionUseCase(
        mem_session, mem_event, mem_intent
    )

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = noop_lifespan

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    app.router.lifespan_context = original_lifespan
