import logging
import re
import subprocess
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)

BROWSER_PROCESSES = {
    "firefox", "firefox-esr", "chrome", "chromium", "chromium-browser",
    "brave", "opera", "edge", "vivaldi",
}


class WindowTracker:
    def __init__(self):
        self._active_window: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()
        logger.info("Window tracker started")

    def _poll(self):
        while self._running:
            try:
                info = self._get_active_window_info()
                if info:
                    with self._lock:
                        self._active_window = info
            except Exception as e:
                logger.debug("Window tracking error: %s", e)

            time.sleep(1)

    def _get_active_window_info(self) -> dict[str, Any] | None:
        result = subprocess.run(
            ["xdotool", "getactivewindow"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None

        window_id = result.stdout.strip()

        title = self._get_xprop(window_id, "WM_NAME")
        pid = self._get_pid(window_id)
        process_name = self._get_process_name(pid) if pid else None

        info: dict[str, Any] = {
            "title": title,
            "pid": pid,
            "process": process_name,
            "window_id": window_id,
        }

        if process_name and process_name.lower() in BROWSER_PROCESSES:
            tab_title = self._get_browser_tab_title(window_id)
            if tab_title:
                info["url"] = self.extract_url_from_title(tab_title)
                info["browser_tab_title"] = tab_title

        return info

    def _get_xprop(self, window_id: str, prop: str) -> str:
        try:
            result = subprocess.run(
                ["xprop", "-id", window_id, prop],
                capture_output=True, text=True, timeout=2,
            )
            if result.returncode == 0 and "=" in result.stdout:
                parts = result.stdout.strip().split("=", 1)
                value = parts[1].strip().strip('"')
                return value
        except Exception:
            pass
        return "unknown"

    def _get_pid(self, window_id: str) -> int | None:
        try:
            result = subprocess.run(
                ["xprop", "-id", window_id, "_NET_WM_PID"],
                capture_output=True, text=True, timeout=2,
            )
            if result.returncode == 0 and "=" in result.stdout:
                pid_str = result.stdout.strip().split("=", 1)[1].strip()
                return int(pid_str)
        except Exception:
            pass
        return None

    def _get_process_name(self, pid: int) -> str | None:
        try:
            result = subprocess.run(
                ["ps", "-p", str(pid), "-o", "comm="],
                capture_output=True, text=True, timeout=1,
            )
            return result.stdout.strip() or None
        except Exception:
            return None

    def _get_browser_tab_title(self, window_id: str) -> str | None:
        try:
            name_result = subprocess.run(
                ["xdotool", "getwindowname", window_id],
                capture_output=True, text=True, timeout=2,
            )
            if name_result.returncode == 0 and name_result.stdout.strip():
                return name_result.stdout.strip()
        except Exception:
            pass
        return None

    def extract_url_from_title(self, title: str) -> str | None:
        url_patterns = [
            r"https?://[^\s]+",
            r"\b[\w.-]+\.(com|org|net|io|dev|app|edu|gov)\S*",
        ]
        for pattern in url_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def get_active_window(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._active_window)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Window tracker stopped")
