import json
import logging
import time
from typing import Any

from google import genai

from backend.config import settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    pass


class LLMService:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_sec: int | None = None,
        max_retries: int | None = None,
    ):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self.timeout_sec = timeout_sec or settings.inference_timeout_sec
        self.max_retries = max_retries or settings.inference_max_retries
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise LLMServiceError(
                    "GEMINI_API_KEY is not configured. "
                    "Set it in the .env file or environment variables."
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate(self, prompt: str) -> str:
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                client = self._get_client()
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
        raw = self.generate(prompt)
        parsed = self._parse_json_response(raw)
        return raw, parsed

    @staticmethod
    def _parse_json_response(raw: str) -> dict[str, Any]:
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
