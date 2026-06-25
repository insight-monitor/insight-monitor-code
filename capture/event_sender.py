"""
ARCH-8: Capture Agent Resilience — EventSender con reintentos y buffer local.
Si el backend no está disponible, los eventos se guardan en un buffer en memoria
y se reenvían automáticamente cuando el API vuelva a estar online.
"""

import logging
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)

# Tamaño máximo del buffer de eventos pendientes (evita uso excesivo de RAM)
MAX_BUFFER_SIZE = 500
# Número de reintentos por evento antes de descartarlo
MAX_RETRIES = 3
# Tiempo base de espera entre reintentos (segundos) — backoff exponencial
RETRY_BASE_DELAY = 1.0


class EventSender:
    """
    Envía eventos al backend con resiliencia:
    - Reintenta con backoff exponencial si la petición falla.
    - Guarda eventos en buffer si el backend está caído.
    - Reenvía el buffer automáticamente en cada llamada a `send()`.
    """

    def __init__(self, api_url: str = "http://localhost:8002"):
        self.api_url = api_url
        self.client = httpx.Client(timeout=10)
        self._buffer: deque[dict] = deque(maxlen=MAX_BUFFER_SIZE)
        self._backend_available = True

    # ── API pública ───────────────────────────────────────────────────────────

    def send(self, data: dict[str, Any]) -> bool:
        """
        Intenta enviar un evento. Si falla, lo guarda en el buffer local.
        También intenta vaciar el buffer de eventos previos pendientes.
        """
        event = self._build_event(data)

        # Primero intenta vaciar el buffer acumulado
        self._flush_buffer()

        # Luego intenta enviar el evento actual
        success = self._send_with_retry(event)
        if not success:
            self._buffer_event(event)

        return success

    def flush(self) -> int:
        """Fuerza el reenvío del buffer completo. Retorna cuántos eventos se enviaron."""
        return self._flush_buffer()

    @property
    def pending_count(self) -> int:
        """Número de eventos pendientes en el buffer local."""
        return len(self._buffer)

    def close(self):
        # Intento final de vaciar el buffer antes de cerrar
        if self._buffer:
            logger.info(
                "EventSender closing — attempting to flush %d buffered events",
                len(self._buffer),
            )
            self._flush_buffer()
        self.client.close()

    # ── Lógica interna ────────────────────────────────────────────────────────

    def _build_event(self, data: dict[str, Any]) -> dict:
        return {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "capture-agent",
            **data,
        }

    def _send_with_retry(self, event: dict, max_retries: int = MAX_RETRIES) -> bool:
        """Envía un evento con backoff exponencial. Retorna True si tuvo éxito."""
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
                # Error HTTP (4xx/5xx) — no reintentar, es un error del cliente
                logger.error(
                    "HTTP error sending event %s: %s", event.get("event_id"), e
                )
                return False
            except httpx.RequestError as e:
                # Error de red — backend caído, reintentar con backoff
                if self._backend_available:
                    logger.warning(
                        "Backend unreachable (attempt %d/%d): %s",
                        attempt, max_retries, e,
                    )
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2  # backoff exponencial: 1s → 2s → 4s

        self._backend_available = False
        return False

    def _buffer_event(self, event: dict):
        """Guarda un evento en el buffer local cuando el backend no está disponible."""
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
        Intenta reenviar todos los eventos del buffer.
        Se detiene si el backend sigue sin responder.
        Retorna el número de eventos enviados exitosamente.
        """
        if not self._buffer:
            return 0

        sent = 0
        failed_events = []

        while self._buffer:
            event = self._buffer.popleft()
            # Solo 1 intento al vaciar el buffer para no bloquear el agente
            success = self._send_with_retry(event, max_retries=1)
            if success:
                sent += 1
            else:
                failed_events.append(event)
                # Si falla el primero, el backend sigue caído — no continuar
                break

        # Devolver los eventos que no se pudieron enviar al frente del buffer
        for event in reversed(failed_events):
            self._buffer.appendleft(event)

        if sent > 0:
            logger.info("Flushed %d buffered events to backend", sent)

        return sent
