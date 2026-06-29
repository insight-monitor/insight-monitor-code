"""
ARCH-8: Capture Agent Resilience — EventSender with retries and local buffer.
If the backend is unavailable, events are saved in an in-memory buffer
and automatically re-sent when the API comes back online.
"""

import logging
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)

# Maximum buffer size for pending events (prevents excessive RAM usage)
MAX_BUFFER_SIZE = 500
# Number of retries per event before discarding it
MAX_RETRIES = 3
# Base delay between retries (seconds) — exponential backoff
RETRY_BASE_DELAY = 1.0


class EventSender:
    """
    Sends events to the backend with resilience:
    - Retries with exponential backoff if the request fails.
    - Saves events to a local buffer if the backend is down.
    - Automatically re-sends the buffer on each call to `send()`.
    """

    def __init__(self, api_url: str = "http://localhost:8002"):
        self.api_url = api_url
        self.client = httpx.Client(timeout=10)
        self._buffer: deque[dict] = deque(maxlen=MAX_BUFFER_SIZE)
        self._backend_available = True

    # ── Public API ────────────────────────────────────────────────────────────

    def send(self, data: dict[str, Any]) -> bool:
        """
        Attempts to send an event. If it fails, saves it to the local buffer.
        Also attempts to flush previously buffered events.
        """
        event = self._build_event(data)

        # First, attempt to flush the accumulated buffer
        self._flush_buffer()

        # Then attempt to send the current event
        success = self._send_with_retry(event)
        if not success:
            self._buffer_event(event)

        return success

    def send_heartbeat(self) -> bool:
        try:
            response = self.client.post(
                f"{self.api_url}/heartbeat",
                json={"source": "capture-agent"},
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.debug("Heartbeat send failed: %s", e)
            return False

    def flush(self) -> int:
        """Forces a re-send of the full buffer. Returns how many events were sent."""
        return self._flush_buffer()

    @property
    def pending_count(self) -> int:
        """Number of pending events in the local buffer."""
        return len(self._buffer)

    def close(self):
        # Final attempt to flush the buffer before closing
        if self._buffer:
            logger.info(
                "EventSender closing — attempting to flush %d buffered events",
                len(self._buffer),
            )
            self._flush_buffer()
        self.client.close()

    # ── Internal logic ────────────────────────────────────────────────────────

    def _build_event(self, data: dict[str, Any]) -> dict:
        return {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "capture-agent",
            **data,
        }

    def _send_with_retry(self, event: dict, max_retries: int = MAX_RETRIES) -> bool:
        """Sends an event with exponential backoff. Returns True on success."""
        delay = RETRY_BASE_DELAY
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.post(
                    f"{self.api_url}/events",
                    json=event,
                )
                response.raise_for_status()
                if not self._backend_available:
                    logger.info("Backend is back online — resuming normal operation")
                    self._backend_available = True
                return True
            except httpx.HTTPStatusError as e:
                # HTTP error (4xx/5xx) — do not retry, it's a client error
                logger.error(
                    "HTTP error sending event %s: %s", event.get("event_id"), e
                )
                return False
            except httpx.RequestError as e:
                # Network error — backend is down, retry with backoff
                if self._backend_available:
                    logger.warning(
                        "Backend unreachable (attempt %d/%d): %s",
                        attempt, max_retries, e,
                    )
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2  # exponential backoff: 1s → 2s → 4s

        self._backend_available = False
        return False

    def _buffer_event(self, event: dict):
        """Saves an event to the local buffer when the backend is unavailable."""
        if len(self._buffer) >= MAX_BUFFER_SIZE:
            dropped = self._buffer.popleft()
            logger.warning(
                "Buffer full — dropping oldest event: %s", dropped.get("event_id")
            )
        self._buffer.append(event)
        logger.debug(
            "Event %s buffered locally (%d pending)",
            event.get("event_id"), len(self._buffer),
        )

    def _flush_buffer(self) -> int:
        """
        Attempts to re-send all events in the buffer.
        Stops if the backend is still unresponsive.
        Returns the number of events successfully sent.
        """
        if not self._buffer:
            return 0

        sent = 0
        failed_events = []

        while self._buffer:
            event = self._buffer.popleft()
            # Only 1 attempt when flushing to avoid blocking the agent
            success = self._send_with_retry(event, max_retries=1)
            if success:
                sent += 1
            else:
                failed_events.append(event)
                # If the first one fails, backend is still down — stop trying
                break

        # Return unsent events to the front of the buffer
        for event in reversed(failed_events):
            self._buffer.appendleft(event)

        if sent > 0:
            logger.info("Flushed %d buffered events to backend", sent)

        return sent
