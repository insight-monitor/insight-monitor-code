"""
ARCH-4: Use Case — InferIntent
Orchestrates intent inference over a closed session.
Depends on ports (Interfaces) and domain services, not on SQLite.
"""

import logging
from typing import Any

from backend.domain.ports.repositories import IEventRepository, ISessionRepository, IIntentRepository

logger = logging.getLogger(__name__)


class InferIntentUseCase:
    def __init__(
        self,
        session_repo: ISessionRepository,
        event_repo: IEventRepository,
        intent_repo: IIntentRepository,
        llm_service: Any,
        prompt_builder: Any,
        intent_parser: Any,
    ):
        self.session_repo = session_repo
        self.event_repo = event_repo
        self.intent_repo = intent_repo
        self.llm = llm_service
        self.prompt_builder = prompt_builder
        self.intent_parser = intent_parser

    def execute_for_session(self, session_id: str) -> Any | None:
        """
        Runs inference for a specific session.
        Returns the created IntentRecord, or None if skipped.
        """
        session = self.session_repo.find_by_id(session_id)
        if not session:
            logger.warning("Session %s not found for inference", session_id)
            return None

        if self.intent_repo.find_by_session(session_id):
            logger.info("Session %s already has intent, skipping", session_id)
            return None

        events = self.event_repo.find_by_session(session_id)
        if not events:
            logger.warning("Session %s has no events, skipping inference", session_id)
            return None

        prompt = self.prompt_builder.build(session, events)
        logger.info("Running inference for session %s (events=%d)", session_id, len(events))

        try:
            raw_text, raw_response = self.llm.generate_structured(prompt)
        except Exception as e:
            logger.error("LLM inference failed for session %s: %s", session_id, e)
            return None

        try:
            intent = self.intent_parser.parse(raw_response, session_id, raw_text=raw_text)
        except Exception as e:
            logger.error("Intent parsing failed for session %s: %s", session_id, e)
            return None

        self.intent_repo.create(intent.model_dump())
        self.session_repo.update(session_id, {
            "session_type": intent.session_type,
            "goal": intent.goal,
            "confidence": intent.goal_confidence,
        })
        logger.info(
            "Intent recorded for session %s: type=%s goal=%s confidence=%.2f",
            session_id, intent.session_type,
            (intent.goal or "N/A")[:60], intent.goal_confidence,
        )
        return intent

    def execute_for_all_closed(self) -> int:
        """Processes all closed sessions without intent. Returns how many were processed."""
        closed = self.session_repo.find_all(status="closed")
        processed = 0
        for session in closed:
            if self.execute_for_session(session["id"]) is not None:
                processed += 1
        if processed:
            logger.info("InferIntent processed %d closed sessions", processed)
        return processed
