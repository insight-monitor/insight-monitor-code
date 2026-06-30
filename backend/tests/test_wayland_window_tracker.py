"""Tests for WaylandWindowTracker — JSON polling + browser URL extraction."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from capture.window_tracker import (
    WaylandWindowTracker,
    create_window_tracker,
    detect_display_server,
)

pytestmark = pytest.mark.unit


class TestWaylandWindowTrackerReadWindowJson:
    """_read_window_json() parses /tmp/insight-window.json correctly."""

    def test_returns_none_when_file_missing(self, tmp_path):
        tracker = WaylandWindowTracker()
        json_path = tmp_path / "insight-window.json"
        with patch("capture.window_tracker.WAYLAND_WINDOW_JSON", str(json_path)):
            result = tracker._read_window_json()
        assert result is None

    def test_returns_parsed_data_when_file_exists(self, tmp_path):
        tracker = WaylandWindowTracker()
        json_path = tmp_path / "insight-window.json"
        json_path.write_text(
            json.dumps(
                {
                    "title": "Terminal",
                    "wm_class": "gnome-terminal-server",
                    "pid": 1234,
                }
            ),
            encoding="utf-8",
        )

        with patch("capture.window_tracker.WAYLAND_WINDOW_JSON", str(json_path)):
            result = tracker._read_window_json()

        assert result == {
            "title": "Terminal",
            "process": "gnome-terminal-server",
            "pid": 1234,
        }

    def test_returns_none_on_malformed_json(self, tmp_path):
        tracker = WaylandWindowTracker()
        json_path = tmp_path / "insight-window.json"
        json_path.write_text("not valid json", encoding="utf-8")

        with patch("capture.window_tracker.WAYLAND_WINDOW_JSON", str(json_path)):
            result = tracker._read_window_json()

        assert result is None

    def test_returns_none_when_title_is_null(self, tmp_path):
        tracker = WaylandWindowTracker()
        json_path = tmp_path / "insight-window.json"
        json_path.write_text(
            json.dumps(
                {
                    "title": None,
                    "wm_class": None,
                    "pid": None,
                }
            ),
            encoding="utf-8",
        )

        with patch("capture.window_tracker.WAYLAND_WINDOW_JSON", str(json_path)):
            result = tracker._read_window_json()

        assert result == {"title": None, "process": None, "pid": None}

    def test_extracts_url_for_browser_processes(self, tmp_path):
        tracker = WaylandWindowTracker()
        json_path = tmp_path / "insight-window.json"
        json_path.write_text(
            json.dumps(
                {
                    "title": "GitHub - insight-monitor - https://github.com/insight-monitor",
                    "wm_class": "firefox",
                    "pid": 5678,
                }
            ),
            encoding="utf-8",
        )

        with patch("capture.window_tracker.WAYLAND_WINDOW_JSON", str(json_path)):
            result = tracker._read_window_json()

        assert result["process"] == "firefox"
        assert result["url"] == "https://github.com/insight-monitor"
        assert (
            result["browser_tab_title"]
            == "GitHub - insight-monitor - https://github.com/insight-monitor"
        )

    def test_no_url_for_non_browser_processes(self, tmp_path):
        tracker = WaylandWindowTracker()
        json_path = tmp_path / "insight-window.json"
        json_path.write_text(
            json.dumps(
                {
                    "title": "Terminal",
                    "wm_class": "gnome-terminal-server",
                    "pid": 1234,
                }
            ),
            encoding="utf-8",
        )

        with patch("capture.window_tracker.WAYLAND_WINDOW_JSON", str(json_path)):
            result = tracker._read_window_json()

        assert "url" not in result
        assert "browser_tab_title" not in result


class TestWaylandWindowTrackerGetActiveWindow:
    """get_active_window() returns latest snapshot."""

    def test_returns_latest_active_window(self, tmp_path):
        tracker = WaylandWindowTracker()
        json_path = tmp_path / "insight-window.json"
        json_path.write_text(
            json.dumps(
                {
                    "title": "Code",
                    "wm_class": "code",
                    "pid": 999,
                }
            ),
            encoding="utf-8",
        )

        with patch("capture.window_tracker.WAYLAND_WINDOW_JSON", str(json_path)):
            data = tracker._read_window_json()
            if data:
                with tracker._lock:
                    tracker._active_window = data
            result = tracker.get_active_window()

        assert result["title"] == "Code"
        assert result["process"] == "code"
        assert result["pid"] == 999

    def test_returns_copy_not_reference(self):
        tracker = WaylandWindowTracker()
        tracker._active_window = {"title": "original"}
        result = tracker.get_active_window()
        result["title"] = "mutated"
        assert tracker.get_active_window()["title"] == "original"


class TestWaylandWindowTrackerMissingJsonWarning:
    """_warn_missing_once() emits a helpful warning but only once."""

    def setup_method(self):
        WaylandWindowTracker._WARNED_MISSING_JSON = False

    def teardown_method(self):
        WaylandWindowTracker._WARNED_MISSING_JSON = False

    def test_warns_only_once_when_called_multiple_times(self, caplog):
        import logging as logging_module

        tracker = WaylandWindowTracker()
        with caplog.at_level(logging_module.WARNING, logger="capture.window_tracker"):
            tracker._warn_missing_once()
            tracker._warn_missing_once()
            tracker._warn_missing_once()

        warnings = [r for r in caplog.records if "install-gnome-extension.sh" in r.getMessage()]
        assert len(warnings) == 1

    def test_warns_with_install_command(self, caplog):
        import logging as logging_module

        tracker = WaylandWindowTracker()
        with caplog.at_level(logging_module.WARNING, logger="capture.window_tracker"):
            tracker._warn_missing_once()

        messages = [r.getMessage() for r in caplog.records]
        assert any("install-gnome-extension.sh" in m for m in messages)
        assert any("log out" in m.lower() or "log back" in m.lower() for m in messages)

    def test_returns_none_and_warns_when_json_file_missing(self, tmp_path, caplog):
        import logging as logging_module

        tracker = WaylandWindowTracker()
        missing = tmp_path / "no-such-file.json"
        with patch("capture.window_tracker.WAYLAND_WINDOW_JSON", str(missing)):
            with caplog.at_level(logging_module.WARNING, logger="capture.window_tracker"):
                result = tracker._read_window_json()
        assert result is None
        assert any("install-gnome-extension.sh" in r.getMessage() for r in caplog.records)


class TestWaylandWindowTrackerLifecycle:
    """start()/stop() thread lifecycle."""

    def test_start_creates_and_starts_thread(self):
        tracker = WaylandWindowTracker()
        tracker.start()
        assert tracker._thread is not None
        assert tracker._thread.is_alive()
        tracker.stop()
        assert not tracker._thread.is_alive()

    def test_double_start_does_not_crash(self):
        tracker = WaylandWindowTracker()
        tracker.start()
        tracker.start()
        tracker.stop()

    def test_stop_without_start_does_not_crash(self):
        tracker = WaylandWindowTracker()
        tracker.stop()

    def test_thread_is_daemon(self):
        tracker = WaylandWindowTracker()
        tracker.start()
        assert tracker._thread is not None
        assert tracker._thread.daemon is True
        tracker.stop()


class TestDetectDisplayServer:
    """detect_display_server() identifies the display server."""

    @patch.dict("os.environ", {"XDG_SESSION_TYPE": "wayland"})
    def test_returns_wayland_when_xdg_is_wayland(self):
        assert detect_display_server() == "wayland"

    @patch.dict("os.environ", {"XDG_SESSION_TYPE": "x11"})
    def test_returns_x11_when_xdg_is_x11(self):
        assert detect_display_server() == "x11"

    @patch.dict("os.environ", {"XDG_SESSION_TYPE": ""})
    def test_returns_x11_when_xdg_is_empty(self):
        assert detect_display_server() == "x11"

    @patch.dict("os.environ", {}, clear=True)
    def test_returns_x11_when_xdg_unset(self):
        assert detect_display_server() == "x11"


class TestCreateWindowTracker:
    """create_window_tracker() factory returns correct tracker type."""

    @patch.dict("os.environ", {"XDG_SESSION_TYPE": "wayland"})
    def test_returns_wayland_tracker_on_wayland(self):
        tracker = create_window_tracker()
        assert isinstance(tracker, WaylandWindowTracker)

    @patch.dict("os.environ", {"XDG_SESSION_TYPE": "x11"})
    def test_returns_window_tracker_on_x11(self):
        tracker = create_window_tracker()
        from capture.window_tracker import WindowTracker

        assert isinstance(tracker, WindowTracker)

    @patch.dict("os.environ", {"XDG_SESSION_TYPE": ""})
    def test_defaults_to_window_tracker(self):
        tracker = create_window_tracker()
        from capture.window_tracker import WindowTracker

        assert isinstance(tracker, WindowTracker)
