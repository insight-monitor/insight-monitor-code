"""
Input frequency monitor for the capture agent.

Tracks clicks-per-minute and keystrokes-per-minute using either:

* ``evdev`` reads from ``/dev/input/event*`` (preferred — works under both
  X11 and native Wayland, including GNOME / KDE / Sway).
* ``pynput`` as an X11/Xwayland fallback (kept for compatibility on systems
  where ``evdev`` is unavailable or the user lacks permission to read
  ``/dev/input/*``).

The Monitor only counts events; it never inspects the actual contents of
keystrokes, satisfying the "frequency only" privacy contract.
"""

from __future__ import annotations

import logging
import os
import select  # at module level so tests can patch it
import threading
import time

logger = logging.getLogger(__name__)

_BACKEND_EVDEV = "evdev"
_BACKEND_PYNPUT = "pynput"
_BACKEND_NONE = "none"

# Standard mouse button key codes. We treat any press of these as a click.
_MOUSE_BUTTON_CODES = {
    272,  # BTN_LEFT
    273,  # BTN_RIGHT
    274,  # BTN_MIDDLE
    275,  # BTN_SIDE
    276,  # BTN_EXTRA
    277,  # BTN_FORWARD
    278,  # BTN_BACK
    330,  # BTN_TOUCH
    331,  # BTN_STYLUS / BTN_TOOL_FINGER
    332,  # BTN_TOOL_DOUBLETAP
}

# Range covered by 'a'..'z' on Linux evdev keyboards.
_LETTER_CODE_OFFSET = 30   # KEY_A
_LETTER_CODE_END = 47       # KEY_0 area lower bound (digit keys also count)


def _is_keyboard_device(caps) -> bool:
    """True if the device exposes keyboard key codes (EV_KEY producing letters)."""
    key_codes = caps.get(1) or set() if 1 in caps else set()
    if not key_codes:
        return False
    # Must produce key events in the letter range — touch screens by themselves.
    return any(_LETTER_CODE_OFFSET <= code <= _LETTER_CODE_END for code in key_codes)


def _is_mouse_button_device(caps) -> bool:
    """True if the device can produce mouse button events."""
    key_codes = caps.get(1) or set() if 1 in caps else set()
    return bool(key_codes & _MOUSE_BUTTON_CODES)


def _classify_event(event) -> str | None:
    """Map an evdev-style event into 'click', 'key', or None.

    'click' covers any mouse button press (value == 1).
    'key' covers letter keys (KEY_A..KEY_9 region) at value == 1.
    None is returned for releases, repeats, modifier keys, or non-key events.
    """
    EV_KEY = 1
    if getattr(event, "type", None) != EV_KEY:
        return None
    if getattr(event, "value", None) != 1:
        return None
    code = getattr(event, "code", None)
    if code in _MOUSE_BUTTON_CODES:
        return "click"
    if code is not None and _LETTER_CODE_OFFSET <= code <= _LETTER_CODE_END:
        return "key"
    return None


class InputMonitor:
    """Background thread that counts clicks and keystrokes per minute.

    The public API (``start`` / ``get_metrics`` / ``stop``) is unchanged so
    existing callers in ``capture/agent.py`` continue to work.
    """

    def __init__(self):
        self._click_count = 0
        self._key_count = 0
        self._lock = threading.Lock()
        self._running = False
        self._start_time = 0.0
        self._thread: threading.Thread | None = None
        self._backend: str = _BACKEND_NONE
        # Time of the last observed input event (click or keypress), or
        # 0.0 if no input has been seen yet. Used by CaptureAgent to
        # implement idle detection (#92).
        self._last_input_at: float = 0.0
        # Total cumulative counts since the monitor started, used by tests
        # and exposed via :meth:`total_count`.
        self._total_clicks: int = 0
        self._total_keys: int = 0

    # ─────────────────────────── lifecycle ────────────────────────────

    def start(self):
        self._running = True
        self._start_time = self._now()
        self._thread = threading.Thread(target=self._monitor, daemon=True)
        self._thread.start()
        logger.info("Input monitor started (backend=%s)", self._backend or "detect")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Input monitor stopped")

    # ─────────────────────────── metrics ──────────────────────────────

    def get_metrics(self) -> dict:
        elapsed = self._now() - self._start_time
        minutes = max(elapsed / 60.0, 0.01)
        with self._lock:
            cpm = self._click_count / minutes
            kpm = self._key_count / minutes
            self._click_count = 0
            self._key_count = 0
        self._start_time = self._now()
        return {
            "clicks_per_min": round(cpm, 1),
            "keystrokes_per_min": round(kpm, 1),
        }

    def backend(self) -> str:
        """Return the backend in use after start(): ``evdev``, ``pynput`` or ``none``."""
        return self._backend

    def seconds_since_last_input(self) -> float | None:
        """Seconds since the last click or key press, or None if no input yet.

        ``idle_for_seconds`` is only meaningful after at least one input
        event has been recorded, otherwise the agent cannot distinguish
        'user is idle since the agent started' from 'the monitor never
        observed any input yet'. Returning ``None`` lets callers pick the
        appropriate starting stance (typically: emit events for the first
        measure window, then optional idle detection afterwards).
        """
        with self._lock:
            ts = self._last_input_at
        if ts <= 0.0:
            return None
        return self._now() - ts

    def has_seen_input(self) -> bool:
        with self._lock:
            return self._last_input_at > 0.0

    def total_count(self) -> dict:
        """Return cumulative counts {clicks, keys} since monitor started."""
        with self._lock:
            return {"clicks": self._total_clicks, "keys": self._total_keys}

    def _record_input(self, kind: str) -> None:
        if kind not in ("click", "key"):
            return
        with self._lock:
            self._last_input_at = self._now()
            if kind == "click":
                self._click_count += 1
                self._total_clicks += 1
            elif kind == "key":
                self._key_count += 1
                self._total_keys += 1

    # ─────────────────────────── private ──────────────────────────────

    def _now(self) -> float:
        return time.time()

    def _monitor(self):
        if self._try_evdev():
            return
        logger.warning(
            "evdev input monitor could not start; falling back to pynput."
        )
        if self._try_pynput():
            return
        logger.error(
            "No input monitor backend is available. input_activity events "
            "will report zeros. On Linux install the python-evdev package "
            "and ensure the user is in the 'input' group "
            "(sudo usermod -aG input $USER; then log out and back in)."
        )
        # Still keep the thread alive so get_metrics() can be used safely,
        # but counters will always be 0.
        self._backend = _BACKEND_NONE
        while self._running:
            time.sleep(0.5)

    # ────────────── evdev backend ──────────────

    def _try_evdev(self) -> bool:
        try:
            from evdev import InputDevice, list_devices  # noqa: F401
        except ImportError as e:
            logger.debug("evdev not importable: %s", e)
            return False

        # Skip virtual devices created by this process if any.
        skip = {int(p) for p in os.environ.get("INSIGHT_INPUT_SKIP", "").split(",") if p.strip().isdigit()}

        keyboards: list = []
        mice: list = []
        try:
            paths = sorted(list_devices())
        except (PermissionError, OSError) as e:
            logger.error(
                "evdev required permission to read /dev/input/ devices: %s. "
                "Add your user to the 'input' group (sudo usermod -aG input $USER) "
                "and log out/back in.",
                e,
            )
            return False
        except Exception as e:  # pragma: no cover - defensive
            logger.error("Failed to enumerate input devices: %s", e)
            return False

        for path in paths:
            try:
                dev = InputDevice(path)
            except (PermissionError, OSError) as e:
                logger.debug("Skipping %s: %s", path, e)
                continue
            except Exception as e:  # pragma: no cover - defensive
                logger.debug("Skipping %s: %s", path, e)
                continue
            if dev.fd in skip:
                continue
            caps = dev.capabilities()
            if not caps:
                continue
            if _is_keyboard_device(caps):
                keyboards.append(dev)
            elif _is_mouse_button_device(caps):
                mice.append(dev)

        if not keyboards and not mice:
            logger.error(
                "No usable /dev/input/ keyboard/mouse devices found for evdev. "
                "Run 'ls -la /dev/input/event*' to confirm permissions."
            )
            return False

        self._backend = _BACKEND_EVDEV
        names = ", ".join(
            f"{d.path}:{getattr(d, 'name', '?')}" for d in keyboards + mice
        )
        logger.info(
            "Input monitor using evdev (%d device(s): %s)",
            len(keyboards) + len(mice),
            names,
        )

        # Read in a busy loop. select() cannot span InputDevices across different
        # fds easily so we poll each in turn with a short timeout.

        devices: dict[int, Any] = {d.fd: d for d in keyboards + mice}
        try:
            while self._running:
                if not devices:
                    break
                readables, _, _ = select.select(devices, [], [], 0.5)
                if not readables:
                    continue
                for fd in readables:
                    dev = devices.get(fd)
                    if dev is None:
                        continue
                    try:
                        self._process_evdev_events(dev)
                    except OSError as e:
                        logger.debug("evdev read on %s failed: %s", dev.path, e)
                        # Device disappeared (e.g. unplugged). Drop it.
                        try:
                            del devices[fd]
                        except KeyError:
                            pass
        finally:
            for dev in devices.values():
                try:
                    dev.close()
                except Exception:  # pragma: no cover - defensive
                    pass
            # On interpreter shutdown some module-level objects may already
            # have been cleared; tolerate that.
        return True

    def _process_evdev_events(self, dev) -> None:
        """Read all pending events from ``dev`` and update counters."""
        for event in dev.read():
            kind = _classify_event(event)
            if kind:
                self._record_input(kind)

    # ────────────── pynput fallback ──────────────

    def _try_pynput(self) -> bool:
        try:
            from pynput import mouse, keyboard  # type: ignore[import-untyped]
        except Exception as e:
            logger.debug("pynput not available: %s", e)
            return False

        try:

            def on_click(_x, _y, _button, _pressed):
                if not _pressed:
                    return
                self._record_input("click")

            def on_press(_key):
                self._record_input("key")

            mouse_listener = mouse.Listener(on_click=on_click)
            keyboard_listener = keyboard.Listener(on_press=on_press)
            mouse_listener.start()
            keyboard_listener.start()
        except Exception as e:
            logger.debug("pynput listener failed to start: %s", e)
            return False

        self._backend = _BACKEND_PYNPUT
        logger.info("Input monitor using pynput backend.")

        try:
            while self._running:
                if not mouse_listener.running or not keyboard_listener.running:
                    break
                time.sleep(0.5)
        finally:
            try:
                mouse_listener.stop()
            except Exception:  # pragma: no cover - defensive
                pass
            try:
                keyboard_listener.stop()
            except Exception:  # pragma: no cover - defensive
                pass
        return True
