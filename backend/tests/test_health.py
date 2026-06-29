"""Tests for the /health and /heartbeat endpoints + module-level heartbeat functions."""
from unittest.mock import patch

import pytest

import backend.routes.health as health_mod

record_agent_heartbeat = health_mod.record_agent_heartbeat
get_agent_status = health_mod.get_agent_status

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def reset_heartbeat_state():
    """Reset the module-level heartbeat state before each test to prevent cross-test pollution."""
    health_mod._agent_last_seen = None


def get_client(client_fixture):
    """Extract TestClient from fixture tuple."""
    return client_fixture[0]


class TestHealthEndpoint:
    """GET /health — server health check."""

    def test_returns_200_with_all_expected_fields(self, client):
        c = get_client(client)
        response = c.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "api_version" in body
        assert "agent" in body
        assert body["agent"]["status"] in ("online", "offline")
        assert "version" in body["agent"]
        assert "last_seen" in body["agent"]

    def test_agent_status_starts_offline(self, client):
        c = get_client(client)
        body = c.get("/health").json()
        assert body["agent"]["status"] == "offline"
        assert body["agent"]["last_seen"] is None

    def test_agent_goes_online_after_heartbeat(self, client):
        c = get_client(client)
        c.post("/heartbeat")
        body = c.get("/health").json()
        assert body["agent"]["status"] == "online"
        assert body["agent"]["last_seen"] is not None

    def test_api_version_in_response(self, client):
        c = get_client(client)
        body = c.get("/health").json()
        assert body["api_version"] is not None


class TestHeartbeatEndpoint:
    """POST /heartbeat — agent heartbeat registration."""

    def test_heartbeat_returns_200(self, client):
        c = get_client(client)
        resp = c.post("/heartbeat")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_heartbeat_then_health_reflects_online(self, client):
        c = get_client(client)
        c.post("/heartbeat")
        body = c.get("/health").json()
        assert body["agent"]["status"] == "online"

    def test_double_heartbeat_keeps_online(self, client):
        c = get_client(client)
        c.post("/heartbeat")
        c.post("/heartbeat")
        body = c.get("/health").json()
        assert body["agent"]["status"] == "online"


class TestAgentStatusFunctions:
    """Direct unit tests for record_agent_heartbeat() and get_agent_status()."""

    def test_get_agent_status_initial_offline(self):
        status = get_agent_status()
        assert status["status"] == "offline"
        assert status["last_seen"] is None

    def test_record_heartbeat_updates_timestamp(self):
        with patch("backend.routes.health.time.time", return_value=1000.0):
            record_agent_heartbeat()
        assert health_mod._agent_last_seen == 1000.0

    def test_agent_online_immediately_after_heartbeat(self):
        with patch("backend.routes.health.time.time", return_value=1000.0):
            record_agent_heartbeat()
        with patch("backend.routes.health.time.time", return_value=1000.0):
            status = get_agent_status()
        assert status["status"] == "online"

    def test_agent_online_within_timeout_window(self):
        with patch("backend.routes.health.time.time", return_value=1000.0):
            record_agent_heartbeat()
        with patch("backend.routes.health.time.time", return_value=1059.999):
            status = get_agent_status()
        assert status["status"] == "online"

    def test_agent_online_at_exact_timeout_boundary(self):
        with patch("backend.routes.health.time.time", return_value=1000.0):
            record_agent_heartbeat()
        with patch("backend.routes.health.time.time", return_value=1060.0):
            status = get_agent_status()
        assert status["status"] == "online"

    def test_agent_offline_past_timeout(self):
        with patch("backend.routes.health.time.time", return_value=1000.0):
            record_agent_heartbeat()
        with patch("backend.routes.health.time.time", return_value=1060.001):
            status = get_agent_status()
        assert status["status"] == "offline"

    def test_agent_offline_well_past_timeout(self):
        with patch("backend.routes.health.time.time", return_value=1000.0):
            record_agent_heartbeat()
        with patch("backend.routes.health.time.time", return_value=2000.0):
            status = get_agent_status()
        assert status["status"] == "offline"

    def test_last_seen_has_iso_format(self):
        with patch("backend.routes.health.time.time", return_value=1000.0):
            record_agent_heartbeat()
        status = get_agent_status()
        assert "T" in status["last_seen"]
        assert status["last_seen"].endswith("Z")

    def test_version_in_status_when_online(self):
        with patch("backend.routes.health.time.time", return_value=1000.0):
            record_agent_heartbeat()
        status = get_agent_status()
        assert "version" in status
        assert status["version"] is not None

    def test_version_in_status_when_offline(self):
        status = get_agent_status()
        assert "version" in status
        assert status["version"] is not None
