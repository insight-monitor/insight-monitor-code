"""Tests for InputMonitor lifecycle, evdev classification, and backend selection."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from capture.input_monitor import (
    InputMonitor,
    _BACKEND_EVDEV,
    _BACKEND_NONE,
    _BACKEND_PYNPUT,
    _classify_event,
    _is_keyboard_device,
    _is_mouse_button_device,
    _MOUSE_BUTTON_CODES,
)

pytestmark = pytest.mark.unit


# ─────────────────────────── device classification ────────────────────────


class TestInputDeviceClassification:
    def test_keyboard_with_letter_keys(self):
        caps = {1: {30, 32, 48}}  # EV_KEY with LETTER and digit codes
        assert _is_keyboard_device(caps) is True

    def test_not_keyboard_without_letters(self):
        caps = {1: {116}}  # Only KEY_POWER
        assert _is_keyboard_device(caps) is False

    def test_empty_caps(self):
        assert _is_keyboard_device({}) is False
        assert _is_mouse_button_device({}) is False

    def test_mouse_button_device(self):
        caps = {1: {272, 273, 274}, 2: {0, 1}}
        assert _is_mouse_button_device(caps) is True

    def test_no_mouse_button_for_keyboard_only(self):
        caps = {1: {30, 32}}
        assert _is_mouse_button_device(caps) is False


# ─────────────────────────── event classification ────────────────────────


class TestClassifyEvent:
    def _e(self, type_, code, value):
        return MagicMock(spec=["type", "code", "value"], type=type_, code=code, value=value)

    def test_mouse_left_click(self):
        e = self._e(1, 272, 1)
        assert _classify_event(e) == "click"

    def test_mouse_release_not_counted(self):
        e = self._e(1, 272, 0)
        assert _classify_event(e) is None

    def test_letter_press(self):
        e = self._e(1, 30, 1)  # KEY_A
        assert _classify_event(e) == "key"

    def test_modifier_key_not_counted(self):
        e = self._e(1, 29, 1)  # KEY_LEFTCTRL = 29
        assert _classify_event(e) is None

    def test_digit_key_counted(self):
        e = self._e(1, 35, 1)  # KEY_9 in the same letter range
        assert _classify_event(e) == "key"

    def test_non_key_event(self):
        e = self._e(2, 0, 1)  # EV_REL movement
        assert _classify_event(e) is None

    def test_all_known_mouse_buttons(self):
        for code in _MOUSE_BUTTON_CODES:
            assert _classify_event(self._e(1, code, 1)) == "click"


# ─────────────────────────── lifecycle ────────────────────────────────


class TestInputMonitorLifecycle:
    def setup_method(self):
        # Ensure pseudo-running state for each test.
        self._started_monitors: list[InputMonitor] = []

    def teardown_method(self):
        for m in self._started_monitors:
            try:
                m.stop()
            except Exception:
                pass

    def test_initial_backend_is_none(self):
        m = InputMonitor()
        assert m.backend() == _BACKEND_NONE

    def test_get_metrics_zero_before_events(self):
        m = InputMonitor()
        import time
        m._start_time = time.time() - 1.0
        result = m.get_metrics()
        assert result == {"clicks_per_min": 0.0, "keystrokes_per_min": 0.0}

    def test_get_metrics_aggregates(self):
        m = InputMonitor()
        import time
        m._start_time = time.time() - 60.0
        with m._lock:
            m._click_count = 12
            m._key_count = 48
        result = m.get_metrics()
        assert 10.0 <= result["clicks_per_min"] <= 13.0
        assert 47.0 <= result["keystrokes_per_min"] <= 50.0
        # Counters reset after read.
        assert m._click_count == 0
        assert m._key_count == 0


# ─────────────────────────── evdev backend ──────────────────────────────


class TestEvdevBackend:
    def _make_device(self, caps, fd=1, name="mock", path="/dev/input/event0"):
        dev = MagicMock()
        dev.path = path
        dev.name = name
        dev.fd = fd
        dev.capabilities.return_value = caps
        return dev

    def test_backend_selected_when_devices_found(self):
        m = InputMonitor()
        caps = {1: {30, 32, 48}}  # keyboard
        dev = self._make_device(caps)

        with patch("evdev.list_devices", return_value=["/dev/input/event0"]), \
             patch("evdev.InputDevice", return_value=dev), \
             patch.object(m, "_running", False):
            result = m._try_evdev()

        assert result is True
        assert m.backend() == _BACKEND_EVDEV

    def test_backend_false_on_no_devices(self):
        m = InputMonitor()
        with patch("evdev.list_devices", return_value=[]):
            assert m._try_evdev() is False
        assert m.backend() != _BACKEND_EVDEV

    def test_backend_false_on_permission_error(self):
        m = InputMonitor()
        with patch("evdev.list_devices", side_effect=PermissionError("blocked")):
            assert m._try_evdev() is False
        assert m.backend() != _BACKEND_EVDEV

    def test_backend_false_on_oserror(self):
        m = InputMonitor()
        with patch("evdev.list_devices", side_effect=OSError("denied")):
            assert m._try_evdev() is False
        assert m.backend() != _BACKEND_EVDEV

    def test_process_evdev_events_counts_clicks_and_keys(self):
        m = InputMonitor()

        def make_event(type_, code, value):
            e = MagicMock()
            e.type = type_
            e.code = code
            e.value = value
            return e

        dev = MagicMock()
        dev.read.return_value = [
            make_event(1, 272, 1),   # click
            make_event(1, 30, 1),    # letter a
            make_event(1, 30, 0),    # release (ignored)
            make_event(1, 29, 1),    # modifier (ignored)
            make_event(2, 0, 1),     # EV_REL (ignored)
        ]

        m._process_evdev_events(dev)

        assert m._click_count == 1
        assert m._key_count == 1

    def test_process_evdev_events_empty_read(self):
        m = InputMonitor()
        dev = MagicMock()
        dev.read.return_value = []
        m._process_evdev_events(dev)
        assert m._click_count == 0
        assert m._key_count == 0


# ─────────────────────────── pynput fallback ───────────────────────────


class TestPynputBackend:
    def test_pynput_used_when_evdev_fails(self):
        m = InputMonitor()

        # Drive _monitor directly while preventing loops.
        called = {"pynput": False}

        def fake_try_pynput(self):
            called["pynput"] = True
            self._backend = _BACKEND_PYNPUT
            return True

        with patch.object(InputMonitor, "_try_evdev", return_value=False), \
             patch.object(InputMonitor, "_try_pynput", fake_try_pynput):
            m._running = True
            m._monitor()

        assert called["pynput"] is True
        assert m.backend() == _BACKEND_PYNPUT

    def test_no_backend_logged_when_all_fail(self):
        m = InputMonitor()
        with patch.object(InputMonitor, "_try_evdev", return_value=False), \
             patch.object(InputMonitor, "_try_pynput", return_value=False):
            m._running = True
            sleeps = {"count": 0}

            def fake_sleep(_):
                sleeps["count"] += 1
                # Break the loop after two iterations to avoid hanging tests.
                if sleeps["count"] >= 2:
                    m._running = False

            with patch("time.sleep", fake_sleep):
                m._monitor()

        assert m.backend() == _BACKEND_NONE
