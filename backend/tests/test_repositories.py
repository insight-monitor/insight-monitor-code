"""Tests for database repositories (Event, Session, Intent) and helpers."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backend.config import settings
from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import (
    EventRepository,
    SessionRepository,
    IntentRepository,
    _parse_json_fields,
)


# ---------------------------------------------------------------------------
# Fixtures — isolated temp database per test
# ---------------------------------------------------------------------------

@pytest.fixture
def db(tmp_path):
    Database.reset()
    db_path = str(tmp_path / "test.db")
    old_path = settings.db_path
    settings.db_path = db_path
    database = Database()
    yield database
    Database.reset()
    settings.db_path = old_path


@pytest.fixture
def event_repo(db):
    return EventRepository(db)


@pytest.fixture
def session_repo(db):
    return SessionRepository(db)


@pytest.fixture
def intent_repo(db):
    return IntentRepository(db)


# ---------------------------------------------------------------------------
# EventRepository
# ---------------------------------------------------------------------------

class TestEventRepository:
    """CRUD operations for raw_events table."""

    def test_should_insert_event_and_retrieve_by_find_recent(self, event_repo):
        event_id = str(uuid4())
        event_repo.insert({
            "event_id": event_id,
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        })
        events = event_repo.find_recent()
        assert len(events) == 1, f"Expected 1 event, got {len(events)}"
        assert events[0]["event_id"] == event_id
        assert events[0]["source"] == "test"

    def test_should_find_events_by_session_id(self, event_repo):
        session_id = str(uuid4())
        event_repo.insert({
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
            "session_id": session_id,
        })
        events = event_repo.find_by_session(session_id)
        assert len(events) == 1
        assert events[0]["session_id"] == session_id

    def test_should_return_empty_list_for_nonexistent_session(self, event_repo):
        assert event_repo.find_by_session("nonexistent") == []

    def test_should_ignore_duplicate_event_id(self, event_repo):
        event_id = str(uuid4())
        event = {
            "event_id": event_id,
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        }
        event_repo.insert(event)
        event_repo.insert(event)
        events = event_repo.find_recent()
        assert len(events) == 1, "Duplicate event_id should be silently ignored"

    def test_should_respect_limit_in_find_recent(self, event_repo):
        for _ in range(5):
            event_repo.insert({
                "event_id": str(uuid4()),
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
            })
        assert len(event_repo.find_recent(3)) == 3
        assert len(event_repo.find_recent(10)) == 5

    def test_should_parse_json_fields_on_retrieval(self, event_repo):
        """Session and intent repos parse JSON strings back to Python objects;
        EventRepository does not, so this only checks raw storage works."""
        event_id = str(uuid4())
        event_repo.insert({
            "event_id": event_id,
            "event_type": "url_context",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
            "url": "https://example.com",
        })
        event = event_repo.find_recent(1)[0]
        assert event["url"] == "https://example.com"


# ---------------------------------------------------------------------------
# SessionRepository
# ---------------------------------------------------------------------------

class TestSessionRepository:
    """CRUD operations for sessions table."""

    def test_should_create_session_and_find_by_id(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        session = session_repo.find_by_id(session_id)
        assert session is not None, "Session should exist after creation"
        assert session["id"] == session_id
        assert session["status"] == "open"

    def test_should_return_none_for_nonexistent_session(self, session_repo):
        assert session_repo.find_by_id("nonexistent") is None

    def test_should_list_all_sessions(self, session_repo):
        session_repo.create({
            "id": str(uuid4()),
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        sessions = session_repo.find_all()
        assert len(sessions) == 1

    def test_should_filter_sessions_by_status(self, session_repo):
        session_repo.create({
            "id": str(uuid4()),
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "closed",
        })
        assert len(session_repo.find_all(status="closed")) == 1
        assert len(session_repo.find_all(status="open")) == 0

    def test_should_update_session_fields(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        session_repo.update(session_id, {"status": "closed", "goal": "finished"})
        session = session_repo.find_by_id(session_id)
        assert session["status"] == "closed"
        assert session["goal"] == "finished"

    def test_should_ignore_unknown_fields_on_update(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        session_repo.update(session_id, {"invalid_field": "value"})
        session = session_repo.find_by_id(session_id)
        assert "invalid_field" not in session

    def test_should_do_nothing_when_update_is_empty(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        session_repo.update(session_id, {})
        assert session_repo.find_by_id(session_id)["status"] == "open"

    def test_should_parse_json_fields_on_retrieval(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "app_sequence": ["code", "firefox"],
            "active_apps": ["code"],
        })
        session = session_repo.find_by_id(session_id)
        assert session["app_sequence"] == ["code", "firefox"], (
            "app_sequence should be parsed from JSON string back to list"
        )


# ---------------------------------------------------------------------------
# IntentRepository
# ---------------------------------------------------------------------------

class TestIntentRepository:
    """CRUD operations for intent_records table."""

    def test_should_create_intent_and_find_by_session(self, db, intent_repo):
        session_id = _seed_session(db)
        record_id = str(uuid4())
        intent_repo.create({
            "record_id": record_id,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_type": "applied_learning",
            "goal": "test goal",
            "goal_confidence": 0.85,
        })
        record = intent_repo.find_by_session(session_id)
        assert record is not None
        assert record["id"] == record_id
        assert record["session_type"] == "applied_learning"
        assert record["goal"] == "test goal"

    def test_should_return_none_for_session_without_intent(self, intent_repo):
        assert intent_repo.find_by_session("nonexistent") is None

    def test_should_parse_json_fields_on_retrieval(self, db, intent_repo):
        session_id = _seed_session(db)
        intent_repo.create({
            "record_id": str(uuid4()),
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_type": "ambiguous",
            "goal": "test",
            "goal_confidence": 0.5,
            "tags": ["python", "test"],
            "evidence": ["evidence 1"],
        })
        record = intent_repo.find_by_session(session_id)
        assert record["tags"] == ["python", "test"]
        assert record["evidence"] == ["evidence 1"]

    def test_should_list_all_intent_records(self, db, intent_repo):
        session_id = _seed_session(db)
        intent_repo.create({
            "record_id": str(uuid4()),
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_type": "ambiguous",
            "goal": "test",
            "goal_confidence": 0.5,
        })
        records = intent_repo.find_all()
        assert len(records) == 1


# ---------------------------------------------------------------------------
# _parse_json_fields helper
# ---------------------------------------------------------------------------

class TestParseJsonFields:
    """Unit tests for the _parse_json_fields utility."""

    def test_should_parse_valid_json_string_to_list(self):
        row = {"data": '["a", "b"]'}
        result = _parse_json_fields(row, ["data"])
        assert result["data"] == ["a", "b"]

    def test_should_leave_invalid_json_as_original_string(self):
        row = {"data": "not json"}
        result = _parse_json_fields(row, ["data"])
        assert result["data"] == "not json"

    def test_should_keep_none_value_as_none(self):
        row = {"data": None}
        result = _parse_json_fields(row, ["data"])
        assert result["data"] is None

    def test_should_keep_non_string_values_unchanged(self):
        row = {"data": 42}
        result = _parse_json_fields(row, ["data"])
        assert result["data"] == 42

    def test_should_parse_empty_json_array(self):
        row = {"data": "[]"}
        result = _parse_json_fields(row, ["data"])
        assert result["data"] == []

    def test_should_only_parse_specified_fields(self):
        row = {"keep": '["a"]', "skip": "raw text"}
        result = _parse_json_fields(row, ["keep"])
        assert result["keep"] == ["a"]
        assert result["skip"] == "raw text"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _seed_session(db) -> str:
    """Insert a minimal session row and return its id."""
    session_id = str(uuid4())
    db.execute(
        "INSERT INTO sessions (id, start_time) VALUES (?, ?)",
        (session_id, datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    return session_id
