"""
pipeline/inference_pipeline.py
--------------------------------
Orquestador concreto del pipeline de inferencia de intención.

Conecta directamente con la infraestructura SQLite a través de los repositorios
y coordina el flujo completo para una sesión:

    SessionRepository → EventRepository → PromptBuilder → LLMService
    → IntentParser → IntentRepository → SessionRepository (update)

A diferencia del use case limpio (InferIntentUseCase), esta clase instancia
sus propias dependencias directamente desde la capa de infraestructura.
Es la implementación concreta pensada para el entorno de producción con SQLite.

Nota: Para pruebas unitarias, las dependencias (llm_service, prompt_builder,
intent_parser) pueden inyectarse en el constructor con mocks.
"""

import logging
from typing import Any

from backend.domain.entities.intent_record import IntentRecord
from backend.pipeline.intent_parser import IntentParser, IntentParserError
from backend.pipeline.prompt_builder import PromptBuilder
from backend.services.llm_service import LLMService, LLMServiceError
from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import EventRepository, IntentRepository, SessionRepository

logger = logging.getLogger(__name__)


class InferencePipeline:
    """
    Pipeline de inferencia de intención acoplado a SQLite.

    Orquesta la secuencia completa: obtener sesión → verificar duplicados →
    obtener eventos → construir prompt → llamar al LLM → parsear respuesta →
    persistir IntentRecord → actualizar sesión.

    Parámetros del constructor
    --------------------------
    db            : Instancia de Database (conexión SQLite activa).
    user_context  : dict opcional con preferencias del usuario para enriquecer el prompt.
    llm_service   : Servicio LLM a usar. Si None, se crea un LLMService con config por defecto.
    prompt_builder: Constructor de prompts. Si None, se crea uno con user_context.
    intent_parser : Parser de respuestas. Si None, se crea un IntentParser por defecto.

    Los tres últimos parámetros permiten inyección de dependencias para testing.
    """

    def __init__(
        self,
        db: Database,
        user_context: dict[str, Any] | None = None,
        llm_service: LLMService | None = None,
        prompt_builder: PromptBuilder | None = None,
        intent_parser: IntentParser | None = None,
    ):
        self.db = db
        # Repositorios de infraestructura: acceso directo a SQLite
        self.session_repo = SessionRepository(db)
        self.event_repo = EventRepository(db)
        self.intent_repo = IntentRepository(db)
        # Dependencias del pipeline; admiten inyección para facilitar tests
        self.llm = llm_service or LLMService()
        self.prompt_builder = prompt_builder or PromptBuilder(user_context)
        self.intent_parser = intent_parser or IntentParser()

    def process_session(self, session_id: str) -> IntentRecord | None:
        """
        Ejecuta el pipeline completo de inferencia para una sesión específica.

        Flujo:
            1. Buscar la sesión; si no existe → retornar None.
            2. Verificar que no exista ya un IntentRecord para esta sesión
               (evitar duplicados).
            3. Obtener los eventos de la sesión; si no hay eventos → retornar None.
            4. Construir el prompt con PromptBuilder.
            5. Llamar al LLM con LLMService.generate_structured.
            6. Parsear la respuesta con IntentParser.
            7. Persistir el IntentRecord en la BD.
            8. Actualizar la sesión con session_type, goal y confidence.

        Parámetros
        ----------
        session_id : ID único de la sesión a procesar.

        Retorna
        -------
        IntentRecord — El registro creado, o None si se omitió por cualquier razón.
        """
        # Paso 1: verificar que la sesión existe
        session = self.session_repo.find_by_id(session_id)
        if not session:
            logger.warning("Session %s not found for inference", session_id)
            return None

        # Paso 2: evitar reprocesar sesiones que ya tienen intent
        existing = self.intent_repo.find_by_session(session_id)
        if existing:
            logger.info("Session %s already has intent record, skipping", session_id)
            return None

        # Paso 3: necesitamos eventos para construir contexto
        events = self.event_repo.find_by_session(session_id)
        if not events:
            logger.warning("Session %s has no events, skipping inference", session_id)
            return None

        # Pasos 4-5: construir prompt y llamar al LLM
        prompt = self.prompt_builder.build(session, events)
        logger.info("Running inference for session %s (events=%d)", session_id, len(events))

        try:
            raw_text, raw_response = self.llm.generate_structured(prompt)
        except LLMServiceError as e:
            logger.error("LLM inference failed for session %s: %s", session_id, e)
            return None

        # Paso 6: convertir la respuesta JSON en un IntentRecord validado
        try:
            intent = self.intent_parser.parse(raw_response, session_id, raw_text=raw_text)
        except IntentParserError as e:
            logger.error("Intent parsing failed for session %s: %s", session_id, e)
            return None

        # Paso 7: persistir el IntentRecord en la base de datos
        self.intent_repo.create(intent.model_dump())
        logger.info(
            "Intent recorded for session %s: type=%s, goal=%s, confidence=%.2f",
            session_id,
            intent.session_type,
            intent.goal[:60] if intent.goal else "N/A",
            intent.goal_confidence,
        )

        # Paso 8: actualizar la sesión con el resultado de la inferencia
        session_updates = {
            "session_type": intent.session_type,
            "goal": intent.goal,
            "confidence": intent.goal_confidence,
        }
        self.session_repo.update(session_id, session_updates)

        return intent

    def process_closed_sessions(self) -> int:
        """
        Procesa todas las sesiones cerradas que aún no tienen IntentRecord.

        Itera sobre las sesiones con status="closed" y llama a process_session
        para cada una. Las sesiones que ya tienen intent o no tienen eventos
        son ignoradas internamente por process_session.

        Retorna
        -------
        int — Número de sesiones efectivamente procesadas (con intent creado).
        """
        closed_sessions = self.session_repo.find_all(status="closed")
        processed = 0

        for session in closed_sessions:
            intent = self.process_session(session["id"])
            if intent is not None:
                processed += 1

        if processed:
            logger.info("Inference pipeline processed %d closed sessions", processed)
        return processed
