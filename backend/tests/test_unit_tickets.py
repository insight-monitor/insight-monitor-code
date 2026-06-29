"""Tests for /tickets endpoints (CRUD + comments + stats)."""
import pytest

pytestmark = pytest.mark.unit


def get_client(client_fixture):
    """Extract TestClient from fixture tuple."""
    return client_fixture[0]


def _create_valid_ticket(client, **overrides):
    body = {"title": "Test ticket", "description": "desc", "priority": "medium"}
    body.update(overrides)
    resp = client.post("/tickets", json=body)
    assert resp.status_code == 200
    return resp.json()


class TestListTickets:
    def test_list_empty_returns_empty(self, client):
        c = get_client(client)
        resp = c.get("/tickets")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tickets"] == []
        assert data["count"] == 0
        assert data["limit"] == 50
        assert data["offset"] == 0

    def test_list_with_pagination(self, client):
        c = get_client(client)
        for i in range(5):
            _create_valid_ticket(c, title=f"ticket-{i}")

        resp = c.get("/tickets?limit=2&offset=0")
        data = resp.json()
        assert data["count"] == 5
        assert len(data["tickets"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0

    def test_list_filters_by_status(self, client):
        c = get_client(client)
        t1 = _create_valid_ticket(c, title="open-1")
        t2 = _create_valid_ticket(c, title="closed-1")
        c.put(f"/tickets/{t2['id']}", json={"status": "closed"})

        resp = c.get("/tickets?status=open")
        data = resp.json()
        assert data["count"] == 1
        assert data["tickets"][0]["id"] == t1["id"]

    def test_list_invalid_status_returns_400(self, client):
        c = get_client(client)
        resp = c.get("/tickets?status=invalid")
        assert resp.status_code == 400


class TestCreateTicket:
    def test_create_returns_ticket_with_id_and_defaults(self, client):
        c = get_client(client)
        resp = c.post("/tickets", json={"title": "New ticket"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "New ticket"
        assert data["status"] == "open"
        assert data["priority"] == "medium"
        assert data["created_by"] == "system"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_with_all_fields(self, client):
        c = get_client(client)
        resp = c.post(
            "/tickets",
            json={
                "title": "Full",
                "description": "Desc",
                "priority": "high",
                "created_by": "alice",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["description"] == "Desc"
        assert data["priority"] == "high"
        assert data["created_by"] == "alice"

    def test_create_invalid_priority_returns_400(self, client):
        c = get_client(client)
        resp = c.post("/tickets", json={"title": "x", "priority": "urgent"})
        assert resp.status_code == 400

    def test_create_without_title_returns_422(self, client):
        c = get_client(client)
        resp = c.post("/tickets", json={"description": "no title"})
        assert resp.status_code == 422


class TestGetTicket:
    def test_returns_ticket_with_empty_comments(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)

        resp = c.get(f"/tickets/{created['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == created["id"]
        assert data["comments"] == []

    def test_returns_404_for_unknown(self, client):
        c = get_client(client)
        resp = c.get("/tickets/unknown")
        assert resp.status_code == 404


class TestUpdateTicket:
    def test_update_title(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)

        resp = c.put(f"/tickets/{created['id']}", json={"title": "Updated"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"

    def test_update_status_and_priority(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)

        resp = c.put(
            f"/tickets/{created['id']}",
            json={"status": "in_progress", "priority": "high"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "in_progress"
        assert data["priority"] == "high"

    def test_update_invalid_status_returns_400(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)

        resp = c.put(f"/tickets/{created['id']}", json={"status": "bogus"})
        assert resp.status_code == 400

    def test_update_invalid_priority_returns_400(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)

        resp = c.put(f"/tickets/{created['id']}", json={"priority": "bogus"})
        assert resp.status_code == 400

    def test_update_unknown_returns_404(self, client):
        c = get_client(client)
        resp = c.put("/tickets/unknown", json={"title": "x"})
        assert resp.status_code == 404

    def test_update_updates_timestamp(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)
        original_updated_at = created["updated_at"]

        resp = c.put(f"/tickets/{created['id']}", json={"title": "new"})
        assert resp.status_code == 200
        assert resp.json()["updated_at"] >= original_updated_at


class TestDeleteTicket:
    def test_delete_returns_status(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)

        resp = c.delete(f"/tickets/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"
        assert resp.json()["ticket_id"] == created["id"]

    def test_delete_then_get_returns_404(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)
        c.delete(f"/tickets/{created['id']}")

        resp = c.get(f"/tickets/{created['id']}")
        assert resp.status_code == 404

    def test_delete_unknown_returns_404(self, client):
        c = get_client(client)
        resp = c.delete("/tickets/unknown")
        assert resp.status_code == 404


class TestStats:
    def test_stats_returns_zero_for_empty_db(self, client):
        c = get_client(client)
        resp = c.get("/tickets/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["open"] == 0
        assert data["in_progress"] == 0
        assert data["resolved"] == 0
        assert data["closed"] == 0

    def test_stats_counts_by_status(self, client):
        c = get_client(client)
        # Create 5 tickets: 1 stays open, 1 transition to in_progress,
        # 1 to resolved, 1 to closed, 1 stays open
        _create_valid_ticket(c, title="open-1")
        _create_valid_ticket(c, title="open-2")
        progress_ticket = _create_valid_ticket(c, title="to-progress")
        resolved_ticket = _create_valid_ticket(c, title="to-resolved")
        closed_ticket = _create_valid_ticket(c, title="to-closed")

        c.put(f"/tickets/{progress_ticket['id']}", json={"status": "in_progress"})
        c.put(f"/tickets/{resolved_ticket['id']}", json={"status": "resolved"})
        c.put(f"/tickets/{closed_ticket['id']}", json={"status": "closed"})

        resp = c.get("/tickets/stats")
        data = resp.json()
        assert data["total"] == 5
        assert data["open"] == 2
        assert data["in_progress"] == 1
        assert data["resolved"] == 1
        assert data["closed"] == 1


class TestComments:
    def test_add_comment_to_ticket(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)

        resp = c.post(f"/tickets/{created['id']}/comments", json={"content": "Hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["content"] == "Hello"
        assert data["ticket_id"] == created["id"]
        assert data["author"] == "system"

    def test_add_comment_with_author(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)

        resp = c.post(
            f"/tickets/{created['id']}/comments",
            json={"content": "Reply", "author": "bob"},
        )
        assert resp.status_code == 200
        assert resp.json()["author"] == "bob"

    def test_get_ticket_returns_comments_in_order(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)
        c.post(f"/tickets/{created['id']}/comments", json={"content": "first"})
        c.post(f"/tickets/{created['id']}/comments", json={"content": "second"})

        resp = c.get(f"/tickets/{created['id']}")
        assert resp.status_code == 200
        comments = resp.json()["comments"]
        assert len(comments) == 2
        assert comments[0]["content"] == "first"
        assert comments[1]["content"] == "second"

    def test_add_comment_to_unknown_returns_404(self, client):
        c = get_client(client)
        resp = c.post("/tickets/unknown/comments", json={"content": "x"})
        assert resp.status_code == 404

    def test_delete_ticket_cascades_comments(self, client):
        c = get_client(client)
        created = _create_valid_ticket(c)
        c.post(f"/tickets/{created['id']}/comments", json={"content": "x"})

        c.delete(f"/tickets/{created['id']}")

        resp = c.post(f"/tickets/{created['id']}/comments", json={"content": "x"})
        assert resp.status_code == 404
