"""Tests for CaptureAgent idle-detection behaviour (#92)."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from capture.agent import CaptureAgent

pytestmark = pytest.mark.unit


class TestCaptureAgentIdleDetection:
    def _build_agent(self, idle_threshold=120):
        agent = CaptureAgent(
            api_url="http://example.test:8002",
            screenshot_dir="/tmp",
            interval=30,
            idle_threshold=idle_threshold,
        )
        # Replace external collaborators so we never touch the real network,
        # the real input backend, or the real screenshot filesystem.
        agent.event_sender = MagicMock()
        agent.window_tracker = MagicMock()
        agent.window_tracker.get_active_window.return_value = {
            "title": "t", "process": "p", "pid": 1, "url": None,
        }
        agent.screenshot_capture = MagicMock()
        agent.screenshot_capture.capture.return_value = Path("/tmp/dummy.png")
        agent.input_monitor = MagicMock()
        agent.input_monitor.get_metrics.return_value = {
            "clicks_per_min": 5.0, "keystrokes_per_min": 10.0,
        }
        return agent

    def test_first_iteration_is_active_until_input_observed(self):
        agent = self._build_agent(idle_threshold=60)
        agent.input_monitor.seconds_since_last_input.return_value = None
        assert agent._is_user_idle() is False

    def test_active_when_idle_for_less_than_threshold(self):
        agent = self._build_agent(idle_threshold=60)
        agent.input_monitor.seconds_since_last_input.return_value = 30.0
        assert agent._is_user_idle() is False

    def test_idle_when_idle_for_more_than_threshold(self):
        agent = self._build_agent(idle_threshold=60)
        agent.input_monitor.seconds_since_last_input.return_value = 120.0
        assert agent._is_user_idle() is True

    def test_idle_threshold_zero_means_disabled(self):
        agent = self._build_agent(idle_threshold=0)
        agent.input_monitor.seconds_since_last_input.return_value = 99999.0
        assert agent._is_user_idle() is False

    def test_idle_marker_emitted_only_on_transition_to_idle(self):
        agent = self._build_agent(idle_threshold=60)
        sent_events = []

        def fake_send(event):
            sent_events.append(event)

        agent.event_sender.send.side_effect = fake_send
        agent._was_idle = False

        # First transition: was not idle, now idle -> emit user_away
        agent._maybe_emit_idle_marker(True)
        # Second iteration: still idle -> no transition, no event
        agent._maybe_emit_idle_marker(True)
        # Third iteration: now active again -> emit user_back
        agent._maybe_emit_idle_marker(False)
        # Fourth iteration: still active -> no transition
        agent._maybe_emit_idle_marker(False)

        user_away_events = [e for e in sent_events if e.get("event_type") == "user_away"]
        user_back_events = [e for e in sent_events if e.get("event_type") == "user_back"]
        assert len(user_away_events) == 1
        assert len(user_back_events) == 1

    def test_first_iteration_does_not_emit_idle_marker(self):
        agent = self._build_agent(idle_threshold=60)
        agent._was_idle = None
        # Even though we'd otherwise consider the user idle, we don't
        # emit a marker for the very first iteration because we don't yet
        # know what the starting state was.
        agent._maybe_emit_idle_marker(True)
        agent.event_sender.send.assert_not_called()

    def test_idle_path_skips_window_focus_and_screenshot(self):
        """When the user is idle, _send_window_event / _send_screenshot_event
        must not be called (but input_activity still is)."""
        agent = self._build_agent(idle_threshold=60)
        agent.running = True
        agent.input_monitor.seconds_since_last_input.return_value = 999.0

        with patch.object(agent, "_send_window_event") as mock_window, \
             patch.object(agent, "_send_screenshot_event") as mock_screen, \
             patch.object(agent, "_send_input_event") as mock_input, \
             patch.object(agent, "_maybe_emit_idle_marker"), \
             patch.object(agent, "_send_heartbeat"), \
             patch("time.sleep", side_effect=lambda _: setattr(agent, "running", False)):
            agent.running = True
            agent.start()

        mock_input.assert_called()
        mock_window.assert_not_called()
        mock_screen.assert_not_called()

    def test_window_and_screenshot_called_when_active(self):
        agent = self._build_agent(idle_threshold=60)

        # Active since input was just observed
        agent.input_monitor.seconds_since_last_input.return_value = 0.0

        with patch.object(agent, "_send_window_event") as mock_window, \
             patch.object(agent, "_send_screenshot_event") as mock_screen, \
             patch.object(agent, "_send_input_event"), \
             patch.object(agent, "_maybe_emit_idle_marker"), \
             patch.object(agent, "_send_heartbeat"), \
             patch("time.sleep", side_effect=lambda _: setattr(agent, "running", False)):
            agent.running = True
            agent.start()

        mock_window.assert_called()
        mock_screen.assert_called()
