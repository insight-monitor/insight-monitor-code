from datetime import datetime, timezone
from uuid import uuid4


class TestCreateEvent:
    def test_create_event(self, client):
        response = client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
            "window_title": "Test Window",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "event_id" in data

    def test_create_event_missing_required(self, client):
        response = client.post("/events", json={})
        assert response.status_code == 422

    def test_create_event_invalid_type(self, client):
        response = client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "bad_type",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        })
        assert response.status_code == 422

    def test_create_event_malformed_json(self, client):
        response = client.post("/events",
                               data="not json",
                               headers={"Content-Type": "application/json"})
        assert response.status_code == 422


class TestListEvents:
    def test_list_events_empty(self, client):
        response = client.get("/events")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["events"] == []

    def test_list_events_with_data(self, client):
        client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        })
        response = client.get("/events")
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_list_events_respects_limit(self, client):
        for _ in range(5):
            client.post("/events", json={
                "event_id": str(uuid4()),
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
            })
        response = client.get("/events?limit=3")
        assert response.json()["count"] == 3


class TestBatchEvents:
    def test_create_batch(self, client):
        response = client.post("/events/batch", json=[
            {
                "event_id": str(uuid4()),
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
            },
            {
                "event_id": str(uuid4()),
                "event_type": "screenshot",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
            },
        ])
        assert response.status_code == 200
        assert response.json()["count"] == 2

    def test_create_batch_empty(self, client):
        response = client.post("/events/batch", json=[])
        assert response.status_code == 200
        assert response.json()["count"] == 0


class TestSessionEvents:
    def test_get_session_events_empty(self, client):
        response = client.get(f"/events/session/{str(uuid4())}")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_get_session_events(self, client):
        session_id = str(uuid4())
        client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
            "session_id": session_id,
        })
        response = client.get(f"/events/session/{session_id}")
        assert response.status_code == 200
        assert response.json()["count"] == 1
