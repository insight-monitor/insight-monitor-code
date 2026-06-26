import logging                    # Standard library logging module
from typing import Any                 # Standard library type hinting for generic types

from backend.domain.entities.intent_record import IntentRecord # Output schema representing inferred intent
from backend.pipeline.intent_parser import IntentParser, IntentParserError # LLM response parsing component and error type
from backend.pipeline.prompt_builder import PromptBuilder # Component that constructs the prompt for LLM
from backend.services.llm_service import LLMService, LLMServiceError # LLM orchestration service and error type
from backend.infrastructure.db.sqlite.database import Database # Database connection component
from backend.infrastructure.db.sqlite.repositories import EventRepository, IntentRepository, SessionRepository # Data repository objects

logger = logging.getLogger(__name__)


# Concrete orchestrator class that executes the session inference pipeline using SQLite repositories
class InferencePipeline:
    def __init__(
        self,
        db: Database,
        user_context: dict[str, Any] | None = None,
        llm_service: LLMService | None = None,
        prompt_builder: PromptBuilder | None = None,
        intent_parser: IntentParser | None = None,
    ):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.event_repo = EventRepository(db)
        self.intent_repo = IntentRepository(db)
        self.llm = llm_service or LLMService()
        self.prompt_builder = prompt_builder or PromptBuilder(user_context)
        self.intent_parser = intent_parser or IntentParser()

    def process_session(self, session_id: str) -> IntentRecord | None:
        # Fetch the session, verify idempotency, query events, request analysis, and persist the output record
        session = self.session_repo.find_by_id(session_id)
        if not session:
            logger.warning("Session %s not found for inference", session_id)
            return None

        # Check if an intent analysis has already been performed to avoid duplicates
        existing = self.intent_repo.find_by_session(session_id)
        if existing:
            logger.info("Session %s already has intent record, skipping", session_id)
            return None

        # Confirm the session is not empty of event items
        events = self.event_repo.find_by_session(session_id)
        if not events:
            logger.warning("Session %s has no events, skipping inference", session_id)
            return None

        # Assemble the formatted LLM query prompt
        prompt = self.prompt_builder.build(session, events)
        logger.info("Running inference for session %s (events=%d)", session_id, len(events))

        # Query the configured LLM API provider
        try:
            raw_text, raw_response = self.llm.generate_structured(prompt)
        except LLMServiceError as e:
            logger.error("LLM inference failed for session %s: %s", session_id, e)
            return None

        # Parse the structured response content
        try:
            intent = self.intent_parser.parse(raw_response, session_id, raw_text=raw_text)
        except IntentParserError as e:
            logger.error("Intent parsing failed for session %s: %s", session_id, e)
            return None

        # Insert new intent record into target DB table
        self.intent_repo.create(intent.model_dump())
        logger.info(
            "Intent recorded for session %s: type=%s, goal=%s, confidence=%.2f",
            session_id,
            intent.session_type,
            intent.goal[:60] if intent.goal else "N/A",
            intent.goal_confidence,
        )

        # Update metadata properties in original session entry
        session_updates = {
            "session_type": intent.session_type,
            "goal": intent.goal,
            "confidence": intent.goal_confidence,
        }
        self.session_repo.update(session_id, session_updates)

        return intent

    def process_closed_sessions(self) -> int:
        # Search all sessions with status value closed and perform inference on each
        closed_sessions = self.session_repo.find_all(status="closed")
        processed = 0

        for session in closed_sessions:
            intent = self.process_session(session["id"])
            if intent is not None:
                processed += 1

        if processed:
            logger.info("Inference pipeline processed %d closed sessions", processed)
        return processed
