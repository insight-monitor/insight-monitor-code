import logging                    # Standard library logging module
from typing import Any                 # Standard library type hinting for generic types

from backend.domain.ports.repositories import IEventRepository, ISessionRepository, IIntentRepository # Port interfaces for repository classes

logger = logging.getLogger(__name__)


# Clean Architecture use case orchestrating the session classification via injected components
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
        # Repositories and pipeline components are injected as parameters
        self.session_repo = session_repo
        self.event_repo = event_repo
        self.intent_repo = intent_repo
        self.llm = llm_service
        self.prompt_builder = prompt_builder
        self.intent_parser = intent_parser

    def execute_for_session(self, session_id: str) -> Any | None:
        # Run classification workflow on the session matching session_id
        session = self.session_repo.find_by_id(session_id)
        if not session:
            logger.warning("Session %s not found for inference", session_id)
            return None

        # Verify idempotency by checking if intent record was already created
        if self.intent_repo.find_by_session(session_id):
            logger.info("Session %s already has intent, skipping", session_id)
            return None

        # Ensure session possesses related events
        events = self.event_repo.find_by_session(session_id)
        if not events:
            logger.warning("Session %s has no events, skipping inference", session_id)
            return None

        # Format prompt payload and query target LLM provider
        prompt = self.prompt_builder.build(session, events)
        logger.info("Running inference for session %s (events=%d)", session_id, len(events))

        try:
            raw_text, raw_response = self.llm.generate_structured(prompt)
        except Exception as e:
            logger.error("LLM inference failed for session %s: %s", session_id, e)
            return None

        # Convert structured payload response dictionary to record entity
        try:
            intent = self.intent_parser.parse(raw_response, session_id, raw_text=raw_text)
        except Exception as e:
            logger.error("Intent parsing failed for session %s: %s", session_id, e)
            return None

        # Store output intent details and synchronize changes on session row
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
        # Batch execute session classification workflow on all closed status sessions
        closed = self.session_repo.find_all(status="closed")
        processed = 0
        for session in closed:
            if self.execute_for_session(session["id"]) is not None:
                processed += 1
        if processed:
            logger.info("InferIntent processed %d closed sessions", processed)
        return processed
