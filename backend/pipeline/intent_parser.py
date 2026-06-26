"""
pipeline/intent_parser.py
--------------------------
Transforma la respuesta JSON del LLM en un IntentRecord validado.

Responsabilidades:
- Validar que la respuesta del LLM contiene los campos obligatorios.
- Verificar que session_type pertenece al conjunto de valores válidos.
- Verificar que los campos de tipo lista (evidence, friction_points, tags)
  sean efectivamente listas.
- Convertir los valores numéricos de forma segura (evitar crashs si el LLM
  devuelve un string donde se espera un float).
- Construir y retornar un IntentRecord con un UUID y timestamp generados aquí.

Este módulo no llama al LLM ni construye prompts; sólo procesa la respuesta.
Si la respuesta es inválida, lanza IntentParserError para que el pipeline
pueda manejar el fallo de forma controlada.
"""

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from backend.domain.entities.intent_record import IntentRecord

logger = logging.getLogger(__name__)


class IntentParserError(Exception):
    """
    Excepción que se lanza cuando la respuesta del LLM no cumple el esquema
    esperado o contiene valores inválidos.

    El pipeline la captura para registrar el error y retornar None en lugar
    de propagar una excepción no controlada.
    """
    pass


class IntentParser:
    """
    Convierte el dict parseado de la respuesta del LLM en un IntentRecord.

    Flujo interno de `parse`:
        1. Validar campos requeridos y tipos (via _validate_response).
        2. Mapear cada campo del dict al campo correspondiente de IntentRecord.
        3. Usar _safe_float para conversiones numéricas resistentes a errores.
        4. Generar record_id (UUID4) y timestamp (UTC now) en este momento.
        5. Retornar el IntentRecord listo para persistir.
    """

    def parse(
        self,
        llm_response: dict[str, Any],
        session_id: str,
        raw_text: str | None = None,
    ) -> IntentRecord:
        """
        Valida y mapea la respuesta del LLM a un IntentRecord.

        Parámetros
        ----------
        llm_response : dict ya parseado desde JSON (resultado de LLMService.generate_structured).
        session_id   : ID de la sesión a la que pertenece este registro.
        raw_text     : Texto crudo original devuelto por el LLM (para trazabilidad/debug).

        Retorna
        -------
        IntentRecord — El objeto de dominio listo para persistir.

        Lanza
        -----
        IntentParserError — Si la respuesta no cumple el esquema mínimo requerido.
        """
        self._validate_response(llm_response)

        record = IntentRecord(
            record_id=str(uuid4()),                            # UUID único generado en tiempo de parsing
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),              # Marca de tiempo UTC del momento de inferencia
            session_type=llm_response.get("session_type", "ambiguous"),
            goal=llm_response.get("goal", ""),
            goal_confidence=self._safe_float(
                llm_response.get("goal_confidence"), 0.0
            ),
            friction_points=llm_response.get("friction_points", []),
            friction_confidence=self._safe_float(
                llm_response.get("friction_confidence")        # None si el LLM no detectó fricción
            ),
            category=llm_response.get("category", "ambiguous"),
            category_confidence=self._safe_float(
                llm_response.get("category_confidence"), 0.0
            ),
            tags=llm_response.get("tags", []),
            evidence=llm_response.get("evidence", []),
            alternatives=llm_response.get("alternatives", []),
            app_summary=llm_response.get("app_summary", {}),
            raw_timeline_summary=llm_response.get("raw_timeline_summary", ""),
            raw_llm_response=raw_text,                         # Guardamos el texto crudo para auditoría
        )

        return record

    @staticmethod
    def _validate_response(response: dict[str, Any]) -> None:
        """
        Verifica que la respuesta del LLM contiene los campos mínimos y tipos correctos.

        Validaciones realizadas:
        1. Presencia de todos los campos required (definidos en OUTPUT_SCHEMA).
        2. Que session_type sea uno de los cinco valores permitidos.
        3. Que evidence sea una lista (no un string ni None).
        4. Que friction_points sea una lista si está presente.
        5. Que tags sea una lista si está presente.

        Parámetros
        ----------
        response : dict con la respuesta JSON del LLM.

        Lanza
        -----
        IntentParserError — Con mensaje descriptivo del primer problema encontrado.
        """
        # Verificar que todos los campos obligatorios estén presentes
        required = [
            "session_type", "goal", "goal_confidence",
            "category", "category_confidence", "evidence",
        ]
        missing = [f for f in required if f not in response]
        if missing:
            raise IntentParserError(
                f"LLM response missing required fields: {missing}"
            )

        # Verificar que session_type sea un valor válido del dominio
        valid_types = {
            "skill_development", "applied_learning",
            "peer_collaboration", "ambiguous", "personal",
        }
        st = response.get("session_type")
        if st not in valid_types:
            raise IntentParserError(
                f"Invalid session_type '{st}'. Must be one of: {valid_types}"
            )

        # evidence debe ser una lista para poder iterar sobre ella de forma segura
        evidence = response.get("evidence")
        if not isinstance(evidence, list):
            raise IntentParserError(
                f"'evidence' must be a list, got {type(evidence).__name__}"
            )

        # friction_points puede ser None (sin fricción), pero si existe debe ser lista
        friction = response.get("friction_points")
        if friction is not None and not isinstance(friction, list):
            raise IntentParserError(
                f"'friction_points' must be a list, got {type(friction).__name__}"
            )

        # tags puede ser None (el LLM lo omitió), pero si existe debe ser lista
        tags = response.get("tags")
        if tags is not None and not isinstance(tags, list):
            raise IntentParserError(
                f"'tags' must be a list, got {type(tags).__name__}"
            )

    @staticmethod
    def _safe_float(value: Any, default: float | None = None) -> float | None:
        """
        Convierte un valor a float de forma segura sin lanzar excepciones.

        Útil para manejar casos donde el LLM devuelve un número como string
        (ej. "0.85") o un valor inesperado (ej. "high").

        Parámetros
        ----------
        value   : El valor a convertir (cualquier tipo).
        default : Valor a retornar si la conversión falla o value es None.
                  Por defecto None.

        Retorna
        -------
        float | None — El valor convertido, o `default` si no se pudo convertir.
        """
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
