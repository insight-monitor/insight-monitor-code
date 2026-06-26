import pytest
from datetime import datetime, timezone

pytestmark = pytest.mark.unit


class TestHealthRoute:
    def test_health_returns_200_with_status(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "agent" in data


class TestEventRoutes:
    def test_create_event_returns_event_id(self, client):
        resp = client.post("/events", json={
            "event_id": "route-ev-1",
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
            "window_title": "Test Window",
            "process_name": "code",
            "pid": 1234,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["event_id"] == "route-ev-1"

    def test_create_event_batch_returns_count(self, client):
        events = []
        for i in range(3):
            events.append({
                "event_id": f"route-batch-{i}",
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
            })
        resp = client.post("/events/batch", json=events)
        assert resp.status_code == 200
        assert resp.json()["count"] == 3

    def test_list_events_returns_empty_when_no_events(self, client):
        resp = client.get("/events?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["events"] == []

    def test_list_events_after_insert(self, client):
        client.post("/events", json={
            "event_id": "route-list-1",
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        })
        resp = client.get("/events?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1

    def test_get_session_events_returns_empty_for_unknown(self, client):
        resp = client.get("/events/session/unknown-session")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["events"] == []


class TestSessionRoutes:
    def test_list_sessions_returns_empty(self, client):
        resp = client.get("/sessions")
        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data
        assert "count" in data

    def test_get_session_returns_404_for_unknown(self, client):
        resp = client.get("/sessions/unknown-session")
        assert resp.status_code == 404

    def test_close_session_returns_404_for_unknown(self, client):
        resp = client.post("/sessions/unknown-session/close")
        assert resp.status_code == 404

    def test_get_session_intent_returns_404_for_unknown(self, client):
        resp = client.get("/sessions/unknown-session/intent")
        assert resp.status_code == 404
