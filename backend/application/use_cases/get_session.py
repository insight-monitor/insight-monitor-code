"""
ARCH-4: Use Case — GetSession
Retrieves the full detail of a session (data + events + intent).
"""

import logging
from typing import Optional

from backend.domain.ports.repositories import IEventRepository, ISessionRepository, IIntentRepository

logger = logging.getLogger(__name__)


class GetSessionUseCase:
    def __init__(
        self,
        session_repo: ISessionRepository,
        event_repo: IEventRepository,
        intent_repo: IIntentRepository,
    ):
        self.session_repo = session_repo
        self.event_repo = event_repo
        self.intent_repo = intent_repo

    def execute(self, session_id: str) -> Optional[dict]:
        """
        Returns the session enriched with events and intent, or None if not found.
        """
        session = self.session_repo.find_by_id(session_id)
        if not session:
            return None

        events = self.event_repo.find_by_session(session_id)
        intent = self.intent_repo.find_by_session(session_id)

        result = dict(session)
        result["events"] = events
        if intent:
            result["intent"] = intent
        return result

    def list_all(self, status: Optional[str] = None, limit: int = 50) -> list[dict]:
        """Lists sessions, optionally filtered by status."""
        return self.session_repo.find_all(status=status, limit=limit)

    def close(self, session_id: str) -> bool:
        """Closes a session. Returns False if not found."""
        session = self.session_repo.find_by_id(session_id)
        if not session:
            return False
        if session.get("status") == "closed":
            return True
        self.session_repo.update(session_id, {"status": "closed"})
        return True
