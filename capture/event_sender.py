import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)


class EventSender:
    def __init__(self, api_url: str = "http://localhost:8002"):
        self.api_url = api_url
        self.client = httpx.Client(timeout=10)

    def send(self, data: dict[str, Any]) -> bool:
        event = {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "capture-agent",
            **data,
        }

        try:
            response = self.client.post(
                f"{self.api_url}/events",
                json=event,
            )
            response.raise_for_status()
            return True
        except httpx.RequestError as e:
            logger.warning("Failed to send event: %s", e)
            return False

    def close(self):
        self.client.close()
