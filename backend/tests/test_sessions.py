"""Tests for /sessions endpoints — list, get, close, intent."""

from datetime import datetime, timezone
from uuid import uuid4

from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import SessionRepository


class TestListSessions:
    """GET /sessions — list all sessions with optional status filter."""

    def test_should_return_empty_list_when_no_sessions_exist(self, client):
        response = client.get("/sessions")
        assert response.status_code == 200
        assert response.json() == {"sessions": [], "count": 0}

    def test_should_return_one_session_after_creating_one(self, client):
        _seed_session()
        response = client.get("/sessions")
        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 1, f"Expected 1 session, got {body['count']}"
        assert len(body["sessions"]) == 1

    def test_should_filter_sessions_by_closed_status(self, client):
        sid = _seed_session()
        _close_session_via_api(client, sid)
        closed = client.get("/sessions?status=closed").json()
        assert closed["count"] == 1
        open_sessions = client.get("/sessions?status=open").json()
        assert open_sessions["count"] == 0

    def test_should_return_empty_list_for_nonexistent_status(self, client):
        response = client.get("/sessions?status=nonexistent")
        assert response.json()["count"] == 0

    def test_should_respect_limit_parameter(self, client):
        for _ in range(3):
            _seed_session()
        response = client.get("/sessions?limit=2")
        assert response.json()["count"] == 2


class TestGetSession:
    """GET /sessions/{id} — single session detail with events."""

    def test_should_return_404_when_session_does_not_exist(self, client):
        response = client.get(f"/sessions/{str(uuid4())}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Session not found"}

    def test_should_return_session_with_events(self, client):
        session_id = _seed_session()
        client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
            "session_id": session_id,
        })
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == session_id
        assert len(body["events"]) == 1, "Session should include its events"
        assert body["status"] == "open"


class TestSessionIntent:
    """GET /sessions/{id}/intent — intent record for a session."""

    def test_should_return_404_when_no_intent_record_exists(self, client):
        session_id = _seed_session()
        response = client.get(f"/sessions/{session_id}/intent")
        assert response.status_code == 404
        assert "No intent record" in response.json()["detail"]


class TestCloseSession:
    """POST /sessions/{id}/close — close an open session."""

    def test_should_close_an_open_session(self, client):
        session_id = _seed_session()
        response = client.post(f"/sessions/{session_id}/close")
        assert response.status_code == 200
        assert response.json() == {
            "status": "closed",
            "session_id": session_id,
        }

    def test_should_return_404_when_closing_nonexistent_session(self, client):
        response = client.post(f"/sessions/{str(uuid4())}/close")
        assert response.status_code == 404
        assert response.json() == {"detail": "Session not found"}

    def test_should_return_already_closed_when_session_already_closed(self, client):
        session_id = _seed_session()
        client.post(f"/sessions/{session_id}/close")
        response = client.post(f"/sessions/{session_id}/close")
        assert response.status_code == 200
        assert response.json() == {
            "status": "already_closed",
            "session_id": session_id,
        }


# ---------------------------------------------------------------------------
# Helpers — build state through the database (session builder is disabled in tests)
# ---------------------------------------------------------------------------

def _seed_session(status: str = "open") -> str:
    """Insert a session directly into the database and return its id."""
    repo = SessionRepository(Database())
    session_id = str(uuid4())
    repo.create({
        "id": session_id,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "status": status,
    })
    return session_id


def _close_session_via_api(client, session_id: str):
    """Close a session through the API."""
    client.post(f"/sessions/{session_id}/close")
