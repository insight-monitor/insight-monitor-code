"""Tests for the /health endpoint."""
import pytest

pytestmark = pytest.mark.unit


class TestHealth:
    """GET /health — server health check."""

    def test_should_return_200_with_status_version_and_agent(self, client):
        response = client.get("/health")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        body = response.json()
        assert body == {
            "status": "ok",
            "agent": "disconnected",
            "version": "0.1.0",
        }, f"Unexpected health response: {body}"
