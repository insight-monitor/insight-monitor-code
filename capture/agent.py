import time
import logging
from pathlib import Path

from capture.window_tracker import WindowTracker
from capture.screenshot_capture import ScreenshotCapture
from capture.input_monitor import InputMonitor
from capture.event_sender import EventSender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaptureAgent:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.screenshot_dir = Path("./data/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        self.window_tracker = WindowTracker()
        self.screenshot_capture = ScreenshotCapture(self.screenshot_dir)
        self.input_monitor = InputMonitor()
        self.event_sender = EventSender(api_url)

        self.interval = 30
        self.running = False

    def start(self):
        self.running = True
        logger.info("Capture agent started")

        self.window_tracker.start()
        self.input_monitor.start()

        last_screenshot = 0.0

        try:
            while self.running:
                now = time.time()

                self._send_window_event()

                if now - last_screenshot >= self.interval:
                    self._send_screenshot_event()
                    last_screenshot = now

                self._send_input_event()

                time.sleep(5)
        except KeyboardInterrupt:
            self.stop()

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
        logger.info("Capture agent stopped")


if __name__ == "__main__":
    agent = CaptureAgent()
    agent.start()
