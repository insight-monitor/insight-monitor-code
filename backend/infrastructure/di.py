"""
ARCH-6: Composition Root — Dependency Injection
Single location where concrete repos and use cases are instantiated.
Routers and the app only import from here; they never touch SQLite directly.
"""

from functools import lru_cache

from backend.config import settings
from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import (
    EventRepository,
    SessionRepository,
    IntentRepository,
)
from backend.domain.ports.repositories import IEventRepository, ISessionRepository, IIntentRepository
from backend.application.use_cases.ingest_event import IngestEventUseCase
from backend.application.use_cases.build_sessions import BuildSessionsUseCase
from backend.application.use_cases.infer_intent import InferIntentUseCase
from backend.application.use_cases.get_session import GetSessionUseCase


# ── Database ──────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_db() -> Database:
    """Single (non-singleton-global) instance of Database, shared across the app."""
    return Database(settings.db_path)


# ── Repositories (Ports → SQLite Infrastructure) ─────────────────────────────

def get_event_repository() -> IEventRepository:
    return EventRepository(get_db())


def get_session_repository() -> ISessionRepository:
    return SessionRepository(get_db())


def get_intent_repository() -> IIntentRepository:
    return IntentRepository(get_db())


# ── Use Cases (Application Layer) ────────────────────────────────────────────

def get_ingest_event_use_case() -> IngestEventUseCase:
    return IngestEventUseCase(get_event_repository())


def get_build_sessions_use_case() -> BuildSessionsUseCase:
    return BuildSessionsUseCase(get_event_repository(), get_session_repository())


def get_get_session_use_case() -> GetSessionUseCase:
    return GetSessionUseCase(
        get_session_repository(),
        get_event_repository(),
        get_intent_repository(),
    )


def get_infer_intent_use_case() -> InferIntentUseCase:
    """
    Builds the InferIntentUseCase injecting LLM services.
    Only instantiated when the API key is available.
    """
    from backend.services.llm_service import LLMService
    from backend.pipeline.prompt_builder import PromptBuilder
    from backend.pipeline.intent_parser import IntentParser

    return InferIntentUseCase(
        session_repo=get_session_repository(),
        event_repo=get_event_repository(),
        intent_repo=get_intent_repository(),
        llm_service=LLMService(),
        prompt_builder=PromptBuilder(),
        intent_parser=IntentParser(),
    )
