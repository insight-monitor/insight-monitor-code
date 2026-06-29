import pytest
from datetime import datetime, timezone

pytestmark = pytest.mark.unit


def get_client(client_fixture):
    """Extract TestClient from fixture tuple."""
    return client_fixture[0]


class TestHealthRoute:
    def test_health_returns_200_with_status(self, client):
        c = get_client(client)
        resp = c.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "api_version" in data
        assert "agent" in data
        assert "status" in data["agent"]
        assert "version" in data["agent"]
        assert "last_seen" in data["agent"]


class TestEventRoutes:
    def test_create_event_returns_event_id(self, client):
        c = get_client(client)
        resp = c.post("/events", json={
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
        c = get_client(client)
        events = []
        for i in range(3):
            events.append({
                "event_id": f"route-batch-{i}",
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
            })
        resp = c.post("/events/batch", json=events)
        assert resp.status_code == 200
        assert resp.json()["count"] == 3

    def test_list_events_returns_empty_when_no_events(self, client):
        c = get_client(client)
        resp = c.get("/events?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["events"] == []

    def test_list_events_after_insert(self, client):
        c = get_client(client)
        c.post("/events", json={
            "event_id": "route-list-1",
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        })
        resp = c.get("/events?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1

    def test_get_session_events_returns_empty_for_unknown(self, client):
        c = get_client(client)
        resp = c.get("/events/session/unknown-session")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["events"] == []


class TestEventPagination:
    def test_get_session_events_paginated(self, client):
        c = get_client(client)
        session_id = "test-session-pagination"
        # Insert 5 events for the session
        for i in range(5):
            c.post("/events", json={
                "event_id": f"pag-{i}",
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
                "session_id": session_id,
            })

        # First page: limit=2, offset=0
        resp = c.get(f"/events/session/{session_id}?limit=2&offset=0")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 5
        assert len(data["events"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
        assert data["events"][0]["event_id"] == "pag-0"
        assert data["events"][1]["event_id"] == "pag-1"

        # Second page: limit=2, offset=2
        resp = c.get(f"/events/session/{session_id}?limit=2&offset=2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 5
        assert len(data["events"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 2
        assert data["events"][0]["event_id"] == "pag-2"
        assert data["events"][1]["event_id"] == "pag-3"

        # Third page: limit=2, offset=4
        resp = c.get(f"/events/session/{session_id}?limit=2&offset=4")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 5
        assert len(data["events"]) == 1
        assert data["events"][0]["event_id"] == "pag-4"

    def test_get_session_events_default_pagination(self, client):
        c = get_client(client)
        session_id = "test-session-default"
        for i in range(3):
            c.post("/events", json={
                "event_id": f"def-{i}",
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
                "session_id": session_id,
            })

        resp = c.get(f"/events/session/{session_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["limit"] == 20  # default
        assert data["offset"] == 0
        assert len(data["events"]) == 3


class TestSessionRoutes:
    def test_list_sessions_returns_empty(self, client):
        c = get_client(client)
        resp = c.get("/sessions")
        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data
        assert "count" in data

    def test_get_session_returns_404_for_unknown(self, client):
        c = get_client(client)
        resp = c.get("/sessions/unknown-session")
        assert resp.status_code == 404

    def test_close_session_returns_404_for_unknown(self, client):
        c = get_client(client)
        resp = c.post("/sessions/unknown-session/close")
        assert resp.status_code == 404

    def test_get_session_intent_returns_404_for_unknown(self, client):
        c = get_client(client)
        resp = c.get("/sessions/unknown-session/intent")
        assert resp.status_code == 404


class TestSessionPagination:
    def test_get_session_detail_paginated(self, client):
        c, mem_event, mem_session, mem_intent = client
        session_id = "test-session-detail"
        mem_session.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "open",
            "event_count": 0,
            "screenshot_count": 0,
            "app_sequence": [],
            "active_apps": [],
        })
        
        # Insert 5 events for the session
        for i in range(5):
            mem_event.insert({
                "event_id": f"detail-{i}",
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
                "session_id": session_id,
                "window_title": f"Window {i}",
                "process_name": "code",
                "pid": 1234,
            })

        # First page: limit=2, offset=0
        resp = c.get(f"/sessions/{session_id}?limit=2&offset=0")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == session_id
        assert data["event_count_total"] == 5
        assert len(data["events"]) == 2
        assert data["events"][0]["event_id"] == "detail-0"
        assert data["events"][1]["event_id"] == "detail-1"

        # Second page: limit=2, offset=2
        resp = c.get(f"/sessions/{session_id}?limit=2&offset=2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["event_count_total"] == 5
        assert len(data["events"]) == 2
        assert data["events"][0]["event_id"] == "detail-2"
        assert data["events"][1]["event_id"] == "detail-3"

        # Third page: limit=2, offset=4
        resp = c.get(f"/sessions/{session_id}?limit=2&offset=4")
        assert resp.status_code == 200
        data = resp.json()
        assert data["event_count_total"] == 5
        assert len(data["events"]) == 1
        assert data["events"][0]["event_id"] == "detail-4"

    def test_get_session_detail_default_pagination(self, client):
        c, mem_event, mem_session, mem_intent = client
        session_id = "test-session-detail-default"
        mem_session.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "open",
            "event_count": 0,
            "screenshot_count": 0,
            "app_sequence": [],
            "active_apps": [],
        })
        
        for i in range(3):
            mem_event.insert({
                "event_id": f"detail-def-{i}",
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
                "session_id": session_id,
            })

        resp = c.get(f"/sessions/{session_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["event_count_total"] == 3
        assert len(data["events"]) == 3
