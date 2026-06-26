"""LLM response parser for intent classification output.

Exports:
    IntentParserError: Exception raised when LLM response validation fails.
    IntentParser: Parser that validates and transforms LLM response to IntentRecord.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from backend.domain.entities.intent_record import IntentRecord


class IntentParserError(Exception):
    """Exception thrown when the LLM structured response is invalid or missing required keys."""
    pass


class IntentParser:
    """Parser component that validates and transforms the LLM dictionary response to IntentRecord."""

    def parse(
        self,
        llm_response: dict[str, Any],
        session_id: str,
        raw_text: str | None = None,
    ) -> IntentRecord:
        """Validate LLM output and instantiate the domain IntentRecord entity.

        Args:
            llm_response: Parsed JSON response from the LLM.
            session_id: Identifier of the analyzed session.
            raw_text: Optional raw LLM response text for debug traceability.

        Returns:
            Validated IntentRecord domain entity.

        Raises:
            IntentParserError: If response is missing required fields or has invalid types.
        """
        self._validate_response(llm_response)

        record = IntentRecord(
            record_id=str(uuid4()),
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),
            session_type=llm_response.get("session_type", "ambiguous"),
            goal=llm_response.get("goal", ""),
            goal_confidence=self._safe_float(
                llm_response.get("goal_confidence"), 0.0
            ),
            friction_points=llm_response.get("friction_points", []),
            friction_confidence=self._safe_float(
                llm_response.get("friction_confidence")
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
            raw_llm_response=raw_text,
        )

        return record

    @staticmethod
    def _validate_response(response: dict[str, Any]) -> None:
        """Check presence and types of all required output properties.

        Args:
            response: Parsed LLM response dictionary.

        Raises:
            IntentParserError: If required fields are missing or have invalid types.
        """
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
        """Convert value to float representation safely returning fallback default on failure.

        Args:
            value: Input value to convert.
            default: Fallback value if conversion fails.

        Returns:
            Float value or default if conversion fails.
        """
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default