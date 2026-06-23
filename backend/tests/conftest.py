from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.config import settings
from backend.storage.database import Database
from backend.storage.repositories import (
    EventRepository,
    SessionRepository,
    IntentRepository,
)


@asynccontextmanager
async def noop_lifespan(_app: FastAPI):
    yield


@pytest.fixture
def client(tmp_path):
    Database.reset()
    db_path = str(tmp_path / "test.db")

    old_path = settings.db_path
    settings.db_path = db_path

    fresh_db = Database.get_instance()

    import backend.routes.events
    import backend.routes.sessions

    backend.routes.events.event_repo = EventRepository(fresh_db)
    backend.routes.sessions.session_repo = SessionRepository(fresh_db)
    backend.routes.sessions.event_repo = EventRepository(fresh_db)
    backend.routes.sessions.intent_repo = IntentRepository(fresh_db)

    from backend.main import app

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = noop_lifespan

    with TestClient(app) as c:
        yield c

    app.router.lifespan_context = original_lifespan
    settings.db_path = old_path
    Database.reset()
