import logging
from typing import Any

from backend.domain.entities.intent_record import IntentRecord
from backend.pipeline.intent_parser import IntentParser, IntentParserError
from backend.pipeline.prompt_builder import PromptBuilder
from backend.services.llm_service import LLMService, LLMServiceError
from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import EventRepository, IntentRepository, SessionRepository

logger = logging.getLogger(__name__)


# Orquestador del pipeline de inferencia que interactúa con SQLite
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
        # Ejecuta el flujo completo de inferencia para una sesión
        session = self.session_repo.find_by_id(session_id)
        if not session:
            logger.warning("Session %s not found for inference", session_id)
            return None

        # Evita procesar sesiones que ya tienen un análisis registrado
        existing = self.intent_repo.find_by_session(session_id)
        if existing:
            logger.info("Session %s already has intent record, skipping", session_id)
            return None

        # Verifica si hay eventos registrados en la sesión
        events = self.event_repo.find_by_session(session_id)
        if not events:
            logger.warning("Session %s has no events, skipping inference", session_id)
            return None

        # Construye el prompt estructurado
        prompt = self.prompt_builder.build(session, events)
        logger.info("Running inference for session %s (events=%d)", session_id, len(events))

        # Realiza la petición estructurada al LLM
        try:
            raw_text, raw_response = self.llm.generate_structured(prompt)
        except LLMServiceError as e:
            logger.error("LLM inference failed for session %s: %s", session_id, e)
            return None

        # Parsea la respuesta obtenida
        try:
            intent = self.intent_parser.parse(raw_response, session_id, raw_text=raw_text)
        except IntentParserError as e:
            logger.error("Intent parsing failed for session %s: %s", session_id, e)
            return None

        # Registra la intención inferida en la base de datos
        self.intent_repo.create(intent.model_dump())
        logger.info(
            "Intent recorded for session %s: type=%s, goal=%s, confidence=%.2f",
            session_id,
            intent.session_type,
            intent.goal[:60] if intent.goal else "N/A",
            intent.goal_confidence,
        )

        # Actualiza los metadatos de clasificación en la sesión
        session_updates = {
            "session_type": intent.session_type,
            "goal": intent.goal,
            "confidence": intent.goal_confidence,
        }
        self.session_repo.update(session_id, session_updates)

        return intent

    def process_closed_sessions(self) -> int:
        # Procesa todas las sesiones con estado cerrado que no tengan análisis
        closed_sessions = self.session_repo.find_all(status="closed")
        processed = 0

        for session in closed_sessions:
            intent = self.process_session(session["id"])
            if intent is not None:
                processed += 1

        if processed:
            logger.info("Inference pipeline processed %d closed sessions", processed)
        return processed
