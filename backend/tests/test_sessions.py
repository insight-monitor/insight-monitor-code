from datetime import datetime, timezone
from uuid import uuid4

from backend.storage.database import Database
from backend.storage.repositories import SessionRepository


def _seed_session(status="open"):
    repo = SessionRepository(Database.get_instance())
    session_id = str(uuid4())
    repo.create({
        "id": session_id,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "status": status,
    })
    return session_id


class TestListSessions:
    def test_empty(self, client):
        response = client.get("/sessions")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_with_data(self, client):
        _seed_session()
        response = client.get("/sessions")
        assert response.status_code == 200
        assert response.json()["count"] >= 1

    def test_filter_by_status(self, client):
        _seed_session(status="closed")
        assert client.get("/sessions?status=closed").json()["count"] >= 1
        assert client.get("/sessions?status=open").json()["count"] == 0

    def test_status_with_no_matches(self, client):
        assert client.get(
            "/sessions?status=nonexistent"
        ).json()["count"] == 0


class TestGetSession:
    def test_not_found(self, client):
        response = client.get(f"/sessions/{str(uuid4())}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    def test_with_events(self, client):
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
        data = response.json()
        assert data["id"] == session_id
        assert len(data["events"]) == 1


class TestSessionIntent:
    def test_not_found(self, client):
        session_id = _seed_session()
        response = client.get(f"/sessions/{session_id}/intent")
        assert response.status_code == 404
        assert "No intent record" in response.json()["detail"]


class TestCloseSession:
    def test_close_open_session(self, client):
        session_id = _seed_session()
        response = client.post(f"/sessions/{session_id}/close")
        assert response.status_code == 200
        assert response.json()["status"] == "closed"

    def test_close_not_found(self, client):
        response = client.post(f"/sessions/{str(uuid4())}/close")
        assert response.status_code == 404

    def test_close_already_closed(self, client):
        session_id = _seed_session(status="closed")
        response = client.post(f"/sessions/{session_id}/close")
        assert response.status_code == 200
        assert response.json()["status"] == "already_closed"
