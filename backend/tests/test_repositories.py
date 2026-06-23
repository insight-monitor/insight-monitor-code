from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backend.config import settings
from backend.storage.database import Database
from backend.storage.repositories import (
    EventRepository,
    SessionRepository,
    IntentRepository,
    _parse_json_fields,
)


@pytest.fixture
def db(tmp_path):
    Database.reset()
    db_path = str(tmp_path / "test.db")
    old_path = settings.db_path
    settings.db_path = db_path
    db = Database.get_instance()
    yield db
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


class TestEventRepository:
    def test_insert_and_find_recent(self, event_repo):
        event_id = str(uuid4())
        event_repo.insert({
            "event_id": event_id,
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        })
        events = event_repo.find_recent()
        assert len(events) == 1
        assert events[0]["event_id"] == event_id

    def test_find_by_session(self, event_repo):
        session_id = str(uuid4())
        event_repo.insert({
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
            "session_id": session_id,
        })
        assert len(event_repo.find_by_session(session_id)) == 1

    def test_find_by_session_empty(self, event_repo):
        assert event_repo.find_by_session("nonexistent") == []

    def test_insert_duplicate_is_ignored(self, event_repo):
        event_id = str(uuid4())
        event = {
            "event_id": event_id,
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        }
        event_repo.insert(event)
        event_repo.insert(event)
        assert len(event_repo.find_recent()) == 1

    def test_find_recent_limit(self, event_repo):
        for _ in range(5):
            event_repo.insert({
                "event_id": str(uuid4()),
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
            })
        assert len(event_repo.find_recent(3)) == 3


class TestSessionRepository:
    def test_create_and_find_by_id(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        session = session_repo.find_by_id(session_id)
        assert session is not None
        assert session["id"] == session_id

    def test_find_by_id_not_found(self, session_repo):
        assert session_repo.find_by_id("nonexistent") is None

    def test_find_all(self, session_repo):
        session_repo.create({
            "id": str(uuid4()),
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        assert len(session_repo.find_all()) == 1

    def test_find_all_filter_by_status(self, session_repo):
        session_repo.create({
            "id": str(uuid4()),
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "closed",
        })
        assert len(session_repo.find_all(status="closed")) == 1
        assert len(session_repo.find_all(status="open")) == 0

    def test_update_session(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        session_repo.update(session_id, {"status": "closed"})
        assert session_repo.find_by_id(session_id)["status"] == "closed"

    def test_update_only_allowed_fields(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        session_repo.update(session_id, {"invalid_field": "value"})
        assert "invalid_field" not in session_repo.find_by_id(session_id)

    def test_json_field_parsing(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "app_sequence": ["code", "firefox"],
            "active_apps": ["code"],
        })
        session = session_repo.find_by_id(session_id)
        assert session["app_sequence"] == ["code", "firefox"]

    def test_update_empty_updates_does_nothing(self, session_repo):
        session_id = str(uuid4())
        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
        })
        session_repo.update(session_id, {})
        session = session_repo.find_by_id(session_id)
        assert session["status"] == "open"


class TestIntentRepository:
    def test_create_and_find_by_session(self, db, intent_repo):
        session_id = str(uuid4())
        db.execute(
            "INSERT INTO sessions (id, start_time) VALUES (?, ?)",
            (session_id, datetime.now(timezone.utc).isoformat()),
        )
        db.commit()
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

    def test_find_by_session_not_found(self, intent_repo):
        assert intent_repo.find_by_session("nonexistent") is None

    def test_json_fields_parsed(self, db, intent_repo):
        session_id = str(uuid4())
        db.execute(
            "INSERT INTO sessions (id, start_time) VALUES (?, ?)",
            (session_id, datetime.now(timezone.utc).isoformat()),
        )
        db.commit()
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

    def test_find_all(self, db, intent_repo):
        session_id = str(uuid4())
        db.execute(
            "INSERT INTO sessions (id, start_time) VALUES (?, ?)",
            (session_id, datetime.now(timezone.utc).isoformat()),
        )
        db.commit()
        intent_repo.create({
            "record_id": str(uuid4()),
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_type": "ambiguous",
            "goal": "test",
            "goal_confidence": 0.5,
        })
        records = intent_repo.find_all()
        assert len(records) >= 1


class TestParseJsonFields:
    def test_valid_json(self):
        row = {"data": '["a", "b"]'}
        result = _parse_json_fields(row, ["data"])
        assert result["data"] == ["a", "b"]

    def test_invalid_json(self):
        row = {"data": "not json"}
        result = _parse_json_fields(row, ["data"])
        assert result["data"] == "not json"

    def test_none_value(self):
        row = {"data": None}
        result = _parse_json_fields(row, ["data"])
        assert result["data"] is None

    def test_non_string_value(self):
        row = {"data": 42}
        result = _parse_json_fields(row, ["data"])
        assert result["data"] == 42
