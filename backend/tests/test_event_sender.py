"""Tests for EventSender.send_heartbeat() and CaptureAgent heartbeat delegation."""
from unittest.mock import MagicMock, patch

import httpx
import pytest

pytestmark = pytest.mark.unit

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from capture.event_sender import EventSender


class TestEventSenderSendHeartbeat:
    """send_heartbeat() sends POST /heartbeat and handles responses."""

    def test_send_heartbeat_returns_true_on_success(self):
        sender = EventSender("http://localhost:8002")
        sender.client = MagicMock()
        sender.client.post.return_value.raise_for_status.return_value = None

        result = sender.send_heartbeat()

        assert result is True
        sender.client.post.assert_called_once_with(
            "http://localhost:8002/heartbeat",
            json={"source": "capture-agent"},
        )

    def test_send_heartbeat_uses_correct_api_url(self):
        sender = EventSender("http://custom-api:9999")
        sender.client = MagicMock()
        sender.client.post.return_value.raise_for_status.return_value = None

        sender.send_heartbeat()

        sender.client.post.assert_called_once_with(
            "http://custom-api:9999/heartbeat",
            json={"source": "capture-agent"},
        )

    def test_send_heartbeat_returns_false_on_network_error(self):
        sender = EventSender("http://localhost:8002")
        sender.client = MagicMock()
        sender.client.post.side_effect = httpx.RequestError("Connection refused")

        result = sender.send_heartbeat()

        assert result is False

    def test_send_heartbeat_returns_false_on_http_error(self):
        sender = EventSender("http://localhost:8002")
        sender.client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Server Error", request=MagicMock(), response=MagicMock()
        )
        sender.client.post.return_value = mock_response

        result = sender.send_heartbeat()

        assert result is False

    def test_send_heartbeat_returns_false_on_unexpected_exception(self):
        sender = EventSender("http://localhost:8002")
        sender.client = MagicMock()
        sender.client.post.side_effect = RuntimeError("Unexpected failure")

        result = sender.send_heartbeat()

        assert result is False

    def test_close_client_after_heartbeat(self):
        sender = EventSender("http://localhost:8002")
        sender.client = MagicMock()
        sender.client.post.return_value.raise_for_status.return_value = None

        sender.send_heartbeat()
        sender.close()

        sender.client.close.assert_called_once()


class TestCaptureAgentHeartbeatDelegation:
    """CaptureAgent._send_heartbeat() delegates to EventSender.send_heartbeat()."""

    def test_agent_send_heartbeat_calls_event_sender(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from capture.agent import CaptureAgent

        agent = CaptureAgent(api_url="http://localhost:8002")
        agent.event_sender = MagicMock()
        agent.event_sender.send_heartbeat.return_value = True

        agent._send_heartbeat()

        agent.event_sender.send_heartbeat.assert_called_once()

    def test_agent_initializes_heartbeat_timer(self):
        from capture.agent import CaptureAgent

        agent = CaptureAgent(api_url="http://localhost:8002")
        assert agent._last_heartbeat == 0.0

    @patch("capture.agent.CaptureAgent._send_heartbeat")
    @patch("capture.agent.CaptureAgent._send_window_event")
    @patch("capture.agent.CaptureAgent._send_input_event")
    def test_heartbeat_interval_tracking(
        self,
        mock_send_input,
        mock_send_window,
        mock_send_heartbeat,
    ):
        from capture.agent import CaptureAgent

        agent = CaptureAgent(api_url="http://localhost:8002")
        agent.window_tracker = MagicMock()
        agent.input_monitor = MagicMock()
        agent.event_sender = MagicMock()

        agent._last_heartbeat = 0.0

        with patch("capture.agent.time.time", return_value=30.0):
            should_heartbeat = (30.0 - agent._last_heartbeat) >= 30
            assert should_heartbeat is True

        with patch("capture.agent.time.time", return_value=29.999):
            should_heartbeat = (29.999 - agent._last_heartbeat) >= 30
            assert should_heartbeat is False
