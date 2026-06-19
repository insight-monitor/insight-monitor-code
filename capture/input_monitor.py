import logging
import threading
import time

logger = logging.getLogger(__name__)


class InputMonitor:
    def __init__(self):
        self._click_count = 0
        self._key_count = 0
        self._lock = threading.Lock()
        self._running = False
        self._start_time = 0.0
        self._thread: threading.Thread | None = None
        self._mouse_listener = None
        self._keyboard_listener = None

    def start(self):
        self._running = True
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._monitor, daemon=True)
        self._thread.start()
        logger.info("Input monitor started")

    def _monitor(self):
        try:
            from pynput import mouse, keyboard

            def on_click(*_):
                with self._lock:
                    self._click_count += 1

            def on_press(*_):
                with self._lock:
                    self._key_count += 1

            self._mouse_listener = mouse.Listener(on_click=on_click)
            self._keyboard_listener = keyboard.Listener(on_press=on_press)

            self._mouse_listener.start()
            self._keyboard_listener.start()

            self._mouse_listener.join()
            self._keyboard_listener.join()
        except Exception as e:
            logger.error("Input monitor error: %s", e)

    def get_metrics(self) -> dict:
        elapsed = time.time() - self._start_time
        minutes = max(elapsed / 60.0, 0.01)

        with self._lock:
            cpm = self._click_count / minutes
            kpm = self._key_count / minutes
            self._click_count = 0
            self._key_count = 0

        self._start_time = time.time()

        return {
            "clicks_per_min": round(cpm, 1),
            "keystrokes_per_min": round(kpm, 1),
        }

    def stop(self):
        self._running = False
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Input monitor stopped")
