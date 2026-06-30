import os
import time
import logging
from pathlib import Path

from capture.window_tracker import create_window_tracker
from capture.screenshot_capture import ScreenshotCapture
from capture.input_monitor import InputMonitor
from capture.event_sender import EventSender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaptureAgent:
    def __init__(
        self,
        api_url: str | None = None,
        screenshot_dir: str | None = None,
        interval: int | None = None,
        idle_threshold: int | None = None,
    ):
        self.api_url = api_url if api_url is not None else os.getenv("API_URL", "http://localhost:8002")
        screenshot_dir_path = screenshot_dir if screenshot_dir is not None else os.getenv(
            "SCREENSHOT_DIR", "./data/screenshots"
        )
        self.screenshot_dir = Path(screenshot_dir_path)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        self.window_tracker = create_window_tracker()
        self.screenshot_capture = ScreenshotCapture(self.screenshot_dir)
        self.input_monitor = InputMonitor()
        self.event_sender = EventSender(self.api_url)

        self.interval = interval or int(os.getenv("CAPTURE_INTERVAL_SECONDS", "30"))
        # When the user has not produced any input for this many seconds,
        # stop window_focus/screenshot sampling and emit a user_away marker.
        # Set to 0 to disable the behaviour entirely.
        self.idle_threshold = (
            idle_threshold
            if idle_threshold is not None
            else int(os.getenv("IDLE_THRESHOLD_SECONDS", "120"))
        )
        self.running = False
        self._last_heartbeat = 0.0
        # Tracking the previous idle state lets us emit user_away/user_back
        # marker events exactly once per transition rather than every loop.
        self._was_idle: bool | None = None

    def _send_heartbeat(self):
        self.event_sender.send_heartbeat()

    def start(self):
        self.running = True
        logger.info(
            "Capture agent started (api=%s, interval=%ds, idle_threshold=%ds)",
            self.api_url,
            self.interval,
            self.idle_threshold,
        )

        self.window_tracker.start()
        self.input_monitor.start()

        last_screenshot = 0.0

        try:
            while self.running:
                now = time.time()
                is_idle = self._is_user_idle()
                self._maybe_emit_idle_marker(is_idle)

                if not is_idle:
                    self._send_window_event()

                    if now - last_screenshot >= self.interval:
                        self._send_screenshot_event()
                        last_screenshot = now
                else:
                    # Keep last_screenshot fresh so a screenshot is taken
                    # immediately after the user comes back.
                    last_screenshot = 0.0

                # Always sample the input activity stream so dashboards see
                # the zero counts and the session builder can still detect
                # activity transitions (#91).
                self._send_input_event()

                if now - self._last_heartbeat >= 30:
                    self._send_heartbeat()
                    self._last_heartbeat = now

                time.sleep(5)
        except KeyboardInterrupt:
            self.stop()

    def _is_user_idle(self) -> bool:
        """True when the user is considered idle right now."""
        if self.idle_threshold <= 0:
            return False
        idle_for = self.input_monitor.seconds_since_last_input()
        if idle_for is None:
            # No input seen yet — cannot prove activity; treat as active so
            # we capture the first period before deciding to go idle.
            return False
        return idle_for >= self.idle_threshold

    def _maybe_emit_idle_marker(self, is_idle: bool):
        """Send a user_away / user_back event iff the idle state changed."""
        prev = self._was_idle
        self._was_idle = is_idle
        if prev is None or prev == is_idle:
            return
        marker = "user_away" if is_idle else "user_back"
        logger.info("User transition detected: %s", marker)
        self.event_sender.send({"event_type": marker})

    def _send_window_event(self):
        window_info = self.window_tracker.get_active_window()
        event = {
            "event_type": "window_focus",
            "window_title": window_info.get("title"),
            "process_name": window_info.get("process"),
            "pid": window_info.get("pid"),
            "url": window_info.get("url"),
        }
        self.event_sender.send(event)

    def _send_screenshot_event(self):
        window_info = self.window_tracker.get_active_window()
        screenshot_path = self.screenshot_capture.capture()
        event = {
            "event_type": "screenshot",
            "window_title": window_info.get("title"),
            "process_name": window_info.get("process"),
            "pid": window_info.get("pid"),
            "screenshot_path": str(screenshot_path) if screenshot_path else None,
        }
        self.event_sender.send(event)

    def _send_input_event(self):
        input_metrics = self.input_monitor.get_metrics()
        event = {
            "event_type": "input_activity",
            "clicks_per_min": input_metrics.get("clicks_per_min"),
            "keystrokes_per_min": input_metrics.get("keystrokes_per_min"),
        }
        self.event_sender.send(event)

    def stop(self):
        self.running = False
        self.window_tracker.stop()
        self.input_monitor.stop()
        self.event_sender.close()
        logger.info("Capture agent stopped")


if __name__ == "__main__":
    agent = CaptureAgent()
    agent.start()
