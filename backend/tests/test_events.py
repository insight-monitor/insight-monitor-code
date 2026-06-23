"""Tests for /events and /events/batch endpoints."""

from datetime import datetime, timezone
from uuid import uuid4


class TestCreateEvent:
    """POST /events — single event ingestion."""

    def test_should_return_200_with_event_id_when_posting_valid_event(self, client):
        event_id = str(uuid4())
        response = client.post("/events", json={
            "event_id": event_id,
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
            "window_title": "Test Window",
        })
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )
        assert response.json() == {"status": "ok", "event_id": event_id}

    def test_should_return_422_when_body_is_empty(self, client):
        response = client.post("/events", json={})
        assert response.status_code == 422, (
            f"Expected 422, got {response.status_code}"
        )

    def test_should_return_422_when_event_type_is_invalid(self, client):
        response = client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "bad_type",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        })
        assert response.status_code == 422

    def test_should_return_422_when_body_is_malformed_json(self, client):
        response = client.post(
            "/events",
            data="not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422


class TestListEvents:
    """GET /events — list recent events with optional limit."""

    def test_should_return_empty_list_when_no_events_exist(self, client):
        response = client.get("/events")
        assert response.status_code == 200
        assert response.json() == {"events": [], "count": 0}

    def test_should_return_one_event_after_creating_one(self, client):
        client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        })
        response = client.get("/events")
        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 1, f"Expected 1 event, got {body['count']}"
        assert len(body["events"]) == 1

    def test_should_respect_limit_parameter(self, client):
        for _ in range(5):
            client.post("/events", json={
                "event_id": str(uuid4()),
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
            })
        response = client.get("/events?limit=3")
        assert response.json()["count"] == 3

    def test_should_return_most_recent_events_first(self, client):
        client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": "2026-01-01T00:00:00",
            "source": "old-event",
        })
        client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": "2026-06-01T00:00:00",
            "source": "recent-event",
        })
        response = client.get("/events")
        events = response.json()["events"]
        assert events[0]["source"] == "recent-event"
        assert events[1]["source"] == "old-event"


class TestBatchEvents:
    """POST /events/batch — ingest multiple events at once."""

    def test_should_create_two_events_and_return_count(self, client):
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
        assert response.json() == {"status": "ok", "count": 2}

    def test_should_accept_empty_batch(self, client):
        response = client.post("/events/batch", json=[])
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "count": 0}

    def test_should_persist_batch_events_for_retrieval(self, client):
        client.post("/events/batch", json=[
            {
                "event_id": str(uuid4()),
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "batch-test",
            },
        ])
        response = client.get("/events")
        assert response.json()["count"] >= 1


class TestSessionEvents:
    """GET /events/session/{session_id} — filter events by session."""

    def test_should_return_empty_list_for_nonexistent_session(self, client):
        response = client.get(f"/events/session/{str(uuid4())}")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_should_return_only_events_for_given_session(self, client):
        session_id = str(uuid4())
        client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
            "session_id": session_id,
        })
        client.post("/events", json={
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        })
        response = client.get(f"/events/session/{session_id}")
        assert response.status_code == 200
        assert response.json()["count"] == 1, (
            "Should only return events matching the session_id"
        )
