"""Abstract interfaces (ports) for external services used by use cases.

These interfaces allow use cases to depend on abstractions rather than
concrete implementations (e.g., specific LLM providers).
"""

from abc import ABC, abstractmethod
from typing import Any


class ILLMService(ABC):
    """Abstract interface for LLM completion services."""

    @abstractmethod
    def generate_structured(self, prompt: str) -> tuple[str, dict[str, Any]]:
        """Generate a structured completion for the given prompt.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            Tuple of (raw_text_response, parsed_json_dict).
        """
        pass

    @abstractmethod
    def _parse_json_response(self, text: str) -> dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks.

        Args:
            text: Raw text response from LLM.

        Returns:
            Parsed JSON as dictionary.

        Raises:
            LLMServiceError: If parsing fails.
        """
        pass


class IPromptBuilder(ABC):
    """Abstract interface for building LLM prompts from session data."""

    @abstractmethod
    def build(self, session: dict[str, Any], events: list[dict[str, Any]]) -> str:
        """Build a prompt for the LLM from session and event data.

        Args:
            session: Session dictionary with metadata.
            events: List of event dictionaries for the session.

        Returns:
            Formatted prompt string.
        """
        pass


class IIntentParser(ABC):
    """Abstract interface for parsing LLM responses into IntentRecord."""

    @abstractmethod
    def parse(
        self,
        llm_response: dict[str, Any],
        session_id: str,
        raw_text: str | None = None
    ) -> Any:
        """Parse LLM response into an IntentRecord.

        Args:
            llm_response: Parsed JSON response from LLM.
            session_id: ID of the session being classified.
            raw_text: Optional raw text response from LLM.

        Returns:
            IntentRecord domain entity.

        Raises:
            IntentParserError: If response is invalid or missing required fields.
        """
        pass