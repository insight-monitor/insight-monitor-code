"""
ARCH-4: Use Case — InferIntent
Orchestrates intent inference over a closed session.
Depends on ports (Interfaces) and domain services, not on SQLite.

application/use_cases/infer_intent.py
---------------------------------------
Implementa el caso de uso InferIntent siguiendo los principios de
Clean Architecture:

- Depende exclusivamente de puertos (interfaces) definidos en domain/ports,
  NO de implementaciones concretas (SQLite, OpenAI, etc.).
- Puede probarse con cualquier implementación mock de los repositorios y servicios.
- Orquesta el mismo flujo lógico que InferencePipeline, pero desacoplado de
  la infraestructura concreta.

Diferencia clave con InferencePipeline
----------------------------------------
InferencePipeline (pipeline/inference_pipeline.py) instancia sus dependencias
directamente desde la infraestructura SQLite. Este use case recibe todas sus
dependencias inyectadas, lo que lo hace portable, testeable y extensible.

Flujo de ejecución para una sesión:
    1. Verificar existencia de la sesión.
    2. Verificar que no exista ya un IntentRecord (idempotencia).
    3. Obtener los eventos de la sesión.
    4. Construir el prompt con el prompt_builder.
    5. Llamar al LLM con llm_service.
    6. Parsear la respuesta con intent_parser.
    7. Persistir el IntentRecord.
    8. Actualizar el estado de la sesión con la inferencia.
"""

import logging
from typing import Any

from backend.domain.ports.repositories import IEventRepository, ISessionRepository, IIntentRepository

logger = logging.getLogger(__name__)


class InferIntentUseCase:
    """
    Caso de uso: inferir la intención del usuario para una sesión cerrada.

    Recibe todas sus dependencias por inyección en el constructor, lo que
    permite sustituir cualquier componente (repositorio, LLM, parser) sin
    modificar este código.

    Parámetros del constructor
    --------------------------
    session_repo   : Repositorio de sesiones (ISessionRepository).
    event_repo     : Repositorio de eventos (IEventRepository).
    intent_repo    : Repositorio de intenciones (IIntentRepository).
    llm_service    : Servicio LLM con método generate_structured(prompt).
    prompt_builder : Builder de prompts con método build(session, events).
    intent_parser  : Parser de respuestas con método parse(response, session_id, raw_text).

    Nota: llm_service, prompt_builder e intent_parser están tipados como Any
    para no acoplar este use case a implementaciones concretas del pipeline.
    """

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

        Paso a paso:
            1. Buscar la sesión en el repositorio; si no existe → None.
            2. Verificar idempotencia: si ya hay intent para esta sesión → None.
            3. Obtener eventos; sin eventos no hay contexto para inferir → None.
            4. Construir prompt y llamar al LLM (genera raw_text y raw_response).
            5. Parsear la respuesta JSON a IntentRecord.
            6. Persistir el intent y actualizar la sesión.

        Parámetros
        ----------
        session_id : ID único de la sesión a inferir.

        Retorna
        -------
        IntentRecord | None — El intent creado, o None si se omitió/falló.
        """
        # Paso 1: la sesión debe existir para poder procesar
        session = self.session_repo.find_by_id(session_id)
        if not session:
            logger.warning("Session %s not found for inference", session_id)
            return None

        # Paso 2: garantizar idempotencia — no duplicar análisis ya existentes
        if self.intent_repo.find_by_session(session_id):
            logger.info("Session %s already has intent, skipping", session_id)
            return None

        # Paso 3: sin eventos no hay señales para el LLM
        events = self.event_repo.find_by_session(session_id)
        if not events:
            logger.warning("Session %s has no events, skipping inference", session_id)
            return None

        # Paso 4: construir el prompt y enviar al LLM
        prompt = self.prompt_builder.build(session, events)
        logger.info("Running inference for session %s (events=%d)", session_id, len(events))

        try:
            raw_text, raw_response = self.llm.generate_structured(prompt)
        except Exception as e:
            logger.error("LLM inference failed for session %s: %s", session_id, e)
            return None

        # Paso 5: convertir la respuesta del LLM en un IntentRecord validado
        try:
            intent = self.intent_parser.parse(raw_response, session_id, raw_text=raw_text)
        except Exception as e:
            logger.error("Intent parsing failed for session %s: %s", session_id, e)
            return None

        # Paso 6: persistir el intent y reflejar los resultados en la sesión
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
        """Processes all closed sessions without intent. Returns how many were processed.

        Itera sobre todas las sesiones con status="closed" y aplica
        execute_for_session a cada una. Las que ya tienen intent o no
        tienen eventos son ignoradas internamente.

        Retorna
        -------
        int — Número de sesiones a las que se les creó un IntentRecord nuevo.
        """
        closed = self.session_repo.find_all(status="closed")
        processed = 0
        for session in closed:
            if self.execute_for_session(session["id"]) is not None:
                processed += 1
        if processed:
            logger.info("InferIntent processed %d closed sessions", processed)
        return processed
