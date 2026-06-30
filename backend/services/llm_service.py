"""LLM service orchestrating prompt completion requests with retry logic."""

import json
import logging
import time
from typing import Any

from backend.config import settings
from backend.domain.ports.services import ILLMService

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Exception raised when the LLM call fails or returns non-parseable output."""
    pass


class LLMService(ILLMService):
    """Service class coordinating LLM prompt completion requests."""

    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_sec: int | None = None,
        max_retries: int | None = None,
    ):
        self.provider = (provider or settings.llm_provider).lower()
        self.api_key = api_key or settings.api_key
        self.model = model or settings.llm_model
        self.timeout_sec = timeout_sec or settings.inference_timeout_sec
        self.max_retries = max_retries or settings.inference_max_retries
        self._client: Any = None

    def _get_client(self) -> Any:
        """Instantiate and cache the API client based on chosen LLM provider."""
        if self._client is not None:
            return self._client

        if not self.api_key:
            raise LLMServiceError(
                "API_KEY is not configured. "
                "Set it in the .env file or environment variables."
            )

        if self.provider == "openai":
            from openai import OpenAI
            kwargs = {"api_key": self.api_key, "timeout": self.timeout_sec}
            if settings.llm_base_url:
                kwargs["base_url"] = settings.llm_base_url
            self._client = OpenAI(**kwargs)
        elif self.provider == "gemini":
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        else:
            raise LLMServiceError(f"Unsupported LLM provider: {self.provider}")

        return self._client

    def generate(self, prompt: str) -> str:
        """Submit the prompt payload with retry attempts using exponential backoff."""
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                client = self._get_client()
                if self.provider == "openai":
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=2048,
                        temperature=0.2,
                        top_p=0.95,
                    )
                    return response.choices[0].message.content
                else:
                    response = client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config={
                            "max_output_tokens": 2048,
                            "temperature": 0.2,
                            "top_p": 0.95,
                        },
                    )
                    return response.text

            except Exception as e:
                last_error = e
                logger.warning(
                    "LLM call attempt %d/%d failed: %s",
                    attempt, self.max_retries, e,
                )
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)

        raise LLMServiceError(
            f"LLM call failed after {self.max_retries} attempts: {last_error}"
        )

    def generate_structured(self, prompt: str) -> tuple[str, dict[str, Any]]:
        """Process generation response text and format it as structured JSON dictionary.

        Returns:
            Tuple of (raw_response_text, parsed_json_dict).
        """
        raw = self.generate(prompt)
        parsed = self._parse_json_response(raw)
        return raw, parsed

    @staticmethod
    def _parse_json_response(raw: str) -> dict[str, Any]:
        """Strip markdown fences if present and deserialize clean string to dictionary."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise LLMServiceError(
                f"Failed to parse LLM response as JSON: {e}\nRaw response: {raw[:500]}"
            )