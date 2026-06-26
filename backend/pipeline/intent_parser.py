import logging                     # Standard library logging module
from datetime import datetime, timezone # Standard library datetime types
from typing import Any                 # Standard library type hinting for generic types
from uuid import uuid4                 # Standard library UUID version 4 generator

from backend.domain.entities.intent_record import IntentRecord # Output schema representing inferred intent


# Exception thrown when the LLM structured response is invalid or missing required keys
class IntentParserError(Exception):
    pass


# Parser component that validates and transforms the LLM dictionary response to IntentRecord
class IntentParser:
    def parse(
        self,
        llm_response: dict[str, Any],
        session_id: str,
        raw_text: str | None = None,
    ) -> IntentRecord:
        # Validate LLM output and instantiate the domain IntentRecord entity
        self._validate_response(llm_response)

        record = IntentRecord(
            record_id=str(uuid4()),                            # Generate a unique record ID
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),              # Set current UTC timestamp
            session_type=llm_response.get("session_type", "ambiguous"),
            goal=llm_response.get("goal", ""),
            goal_confidence=self._safe_float(
                llm_response.get("goal_confidence"), 0.0
            ),
            friction_points=llm_response.get("friction_points", []),
            friction_confidence=self._safe_float(
                llm_response.get("friction_confidence")        # Return None if not found
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
            raw_llm_response=raw_text,                         # Store raw text for debug traceability
        )

        return record

    @staticmethod
    def _validate_response(response: dict[str, Any]) -> None:
        # Check presence and types of all required output properties
        required = [
            "session_type", "goal", "goal_confidence",
            "category", "category_confidence", "evidence",
        ]
        missing = [f for f in required if f not in response]
        if missing:
            raise IntentParserError(
                f"LLM response missing required fields: {missing}"
            )

        valid_types = {
            "skill_development", "applied_learning",
            "peer_collaboration", "ambiguous", "personal",
        }
        st = response.get("session_type")
        if st not in valid_types:
            raise IntentParserError(
                f"Invalid session_type '{st}'. Must be one of: {valid_types}"
            )

        evidence = response.get("evidence")
        if not isinstance(evidence, list):
            raise IntentParserError(
                f"'evidence' must be a list, got {type(evidence).__name__}"
            )

        friction = response.get("friction_points")
        if friction is not None and not isinstance(friction, list):
            raise IntentParserError(
                f"'friction_points' must be a list, got {type(friction).__name__}"
            )

        tags = response.get("tags")
        if tags is not None and not isinstance(tags, list):
            raise IntentParserError(
                f"'tags' must be a list, got {type(tags).__name__}"
            )

    @staticmethod
    def _safe_float(value: Any, default: float | None = None) -> float | None:
        # Convert value to float representation safely returning fallback default on failure
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
