"""
ARCH-11: Unit tests with mocks (InMemory repos)
Verifies Use Cases in complete isolation — no SQLite, no network.
These tests should run in < 2 seconds total.
"""

import pytest
from datetime import datetime, timezone, timedelta

# All tests in this module run with: pytest -m unit
pytestmark = pytest.mark.unit

from backend.infrastructure.db.in_memory.repositories import (
    InMemoryEventRepository,
    InMemorySessionRepository,
    InMemoryIntentRepository,
)
from backend.application.use_cases.ingest_event import IngestEventUseCase
from backend.application.use_cases.build_sessions import BuildSessionsUseCase
from backend.application.use_cases.get_session import GetSessionUseCase
from backend.domain.entities.raw_event import RawEvent, EventType


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_event(event_id="ev-001", process="firefox", session_id=None):
    return {
        "event_id": event_id,
        "event_type": "focus",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "capture-agent",
        "window_title": "Test Window",
        "process_name": process,
        "pid": 1234,
        "screenshot_path": None,
        "screenshot_thumbnail": None,
        "clicks_per_min": 5.0,
        "keystrokes_per_min": 20.0,
        "url": None,
        "browser_tab_title": None,
        "session_id": session_id,
        "session_boundary_type": None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tests: IngestEventUseCase
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestIngestEventUseCase:
    def test_insert_single_event_returns_event_id(self, event_repo):
        # Arrange
        raw = RawEvent(
            event_id="ev-test-01",
            event_type=EventType.focus,
            timestamp=datetime.now(timezone.utc),
            source="capture-agent",
            window_title="Test",
            process_name="code",
        )
        use_case = IngestEventUseCase(event_repo)

        # Act
        result = use_case.execute(raw)

        # Assert
        assert result == "ev-test-01"
        assert len(event_repo.find_recent()) == 1

    def test_insert_batch_returns_count(self, event_repo):
        events = [
            RawEvent(
                event_id=f"ev-batch-{i}",
                event_type=EventType.focus,
                timestamp=datetime.now(timezone.utc),
                source="capture-agent",
            )
            for i in range(5)
        ]
        use_case = IngestEventUseCase(event_repo)
        count = use_case.execute_batch(events)
        assert count == 5
        assert len(event_repo.find_recent()) == 5

    def test_duplicate_event_not_inserted_twice(self, event_repo):
        raw = RawEvent(
            event_id="ev-dup",
            event_type=EventType.focus,
            timestamp=datetime.now(timezone.utc),
            source="capture-agent",
        )
        use_case = IngestEventUseCase(event_repo)
        use_case.execute(raw)
        use_case.execute(raw)  # duplicate
        assert len(event_repo.find_recent()) == 1


# ─────────────────────────────────────────────────────────────────────────────
# Tests: BuildSessionsUseCase
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestBuildSessionsUseCase:
    def test_no_events_returns_zero(self, event_repo, session_repo):
        use_case = BuildSessionsUseCase(event_repo, session_repo)
        result = use_case.execute()
        assert result == 0

    def test_single_unassigned_event_creates_session(self, event_repo, session_repo):
        event_repo.insert(_make_event("ev-001"))
        use_case = BuildSessionsUseCase(event_repo, session_repo)

        use_case.execute()

        sessions = session_repo.find_all()
        assert len(sessions) == 1
        assert sessions[0]["status"] == "open"

    def test_event_assigned_to_existing_session(self, event_repo, session_repo):
        # Create an open session manually
        now = datetime.now(timezone.utc)
        session_repo.create({
            "id": "session-abc",
            "start_time": (now - timedelta(minutes=2)).isoformat(),
            "end_time": (now - timedelta(minutes=1)).isoformat(),
            "status": "open",
            "event_count": 1,
            "screenshot_count": 0,
            "app_sequence": [],
            "active_apps": [],
        })
        event_repo.insert(_make_event("ev-002"))

        use_case = BuildSessionsUseCase(event_repo, session_repo)
        use_case.execute()

        # Should not create a new session — just assign to the existing one
        sessions = session_repo.find_all()
        assert len(sessions) == 1
        assert sessions[0]["id"] == "session-abc"

    def test_close_session_sets_status(self, event_repo, session_repo):
        session_repo.create({
            "id": "session-xyz", "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "open", "event_count": 0, "screenshot_count": 0,
            "app_sequence": [], "active_apps": [],
        })
        use_case = BuildSessionsUseCase(event_repo, session_repo)
        closed = use_case.close_session("session-xyz")
        assert closed is True
        assert session_repo.find_by_id("session-xyz")["status"] == "closed"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: GetSessionUseCase
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestGetSessionUseCase:
    def test_returns_none_for_unknown_session(self, event_repo, session_repo, intent_repo):
        use_case = GetSessionUseCase(session_repo, event_repo, intent_repo)
        assert use_case.execute("does-not-exist") is None

    def test_returns_session_with_events(self, event_repo, session_repo, intent_repo):
        sid = "session-123"
        session_repo.create({
            "id": sid, "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "open", "event_count": 1, "screenshot_count": 0,
            "app_sequence": [], "active_apps": [],
        })
        event = _make_event("ev-A", session_id=sid)
        event_repo.insert(event)

        use_case = GetSessionUseCase(session_repo, event_repo, intent_repo)
        result = use_case.execute(sid)

        assert result is not None
        assert result["id"] == sid
        assert len(result["events"]) == 1

    def test_list_all_filters_by_status(self, event_repo, session_repo, intent_repo):
        now = datetime.now(timezone.utc).isoformat()
        session_repo.create({"id": "s-open", "start_time": now, "status": "open", "event_count": 0, "screenshot_count": 0, "app_sequence": [], "active_apps": []})
        session_repo.create({"id": "s-closed", "start_time": now, "status": "closed", "event_count": 0, "screenshot_count": 0, "app_sequence": [], "active_apps": []})

        use_case = GetSessionUseCase(session_repo, event_repo, intent_repo)
        open_sessions = use_case.list_all(status="open")
        assert len(open_sessions) == 1
        assert open_sessions[0]["id"] == "s-open"
