"""Tests for the /health endpoint."""
import pytest

pytestmark = pytest.mark.unit


def get_client(client_fixture):
    """Extract TestClient from fixture tuple."""
    return client_fixture[0]


class TestHealth:
    """GET /health — server health check."""

    def test_should_return_200_with_status_version_and_agent(self, client):
        c = get_client(client)
        response = c.get("/health")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        body = response.json()
        assert body["status"] == "ok"
        assert "api_version" in body
        assert "agent" in body
        assert body["agent"]["status"] in ("online", "disconnected", "offline")
        assert "version" in body["agent"]
        assert "last_seen" in body["agent"]
