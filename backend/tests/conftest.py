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
    InMemoryTicketRepository,
    InMemoryCommentRepository,
)
from backend.infrastructure.di import (
    get_event_repository,
    get_session_repository,
    get_intent_repository,
    get_ticket_repository,
    get_comment_repository,
    get_ingest_event_use_case,
    get_get_session_use_case,
    get_manage_tickets_use_case,
)
from backend.application.use_cases.manage_tickets import ManageTicketsUseCase


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


@pytest.fixture()
def ticket_repo():
    return InMemoryTicketRepository()


@pytest.fixture()
def comment_repo():
    return InMemoryCommentRepository()


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
    mem_ticket = InMemoryTicketRepository()
    mem_comment = InMemoryCommentRepository()

    from backend.main import app
    from backend.application.use_cases.ingest_event import IngestEventUseCase
    from backend.application.use_cases.get_session import GetSessionUseCase

    app.dependency_overrides[get_event_repository] = lambda: mem_event
    app.dependency_overrides[get_session_repository] = lambda: mem_session
    app.dependency_overrides[get_intent_repository] = lambda: mem_intent
    app.dependency_overrides[get_ticket_repository] = lambda: mem_ticket
    app.dependency_overrides[get_comment_repository] = lambda: mem_comment
    app.dependency_overrides[get_ingest_event_use_case] = lambda: IngestEventUseCase(mem_event)
    app.dependency_overrides[get_get_session_use_case] = lambda: GetSessionUseCase(
        mem_session, mem_event, mem_intent
    )
    app.dependency_overrides[get_manage_tickets_use_case] = lambda: ManageTicketsUseCase(
        mem_ticket, mem_comment
    )

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = noop_lifespan

    with TestClient(app) as c:
        yield c, mem_event, mem_session, mem_intent, mem_ticket, mem_comment

    app.dependency_overrides.clear()
    app.router.lifespan_context = original_lifespan


@pytest.fixture()
def test_repos(client):
    """Returns the in-memory repos used by the client fixture."""
    return client[1], client[2], client[3]
