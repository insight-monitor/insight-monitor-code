import json
import logging
import time
from typing import Any

from backend.config import settings

logger = logging.getLogger(__name__)


# Excepción lanzada ante fallos en la llamada o el parseo del LLM
class LLMServiceError(Exception):
    pass


# Servicio para interactuar con proveedores de LLM (OpenAI y Gemini)
class LLMService:
    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_sec: int | None = None,
        max_retries: int | None = None,
    ):
        # Lee la configuración global o usa los parámetros explícitos
        self.provider = (provider or settings.llm_provider).lower()
        self.api_key = api_key or settings.api_key
        self.model = model or settings.llm_model
        self.timeout_sec = timeout_sec or settings.inference_timeout_sec
        self.max_retries = max_retries or settings.inference_max_retries
        self._client: Any = None  # Inicializado de forma lazy

    def _get_client(self) -> Any:
        # Retorna el cliente del proveedor instanciado de forma lazy (singleton)
        if self._client is not None:
            return self._client

        if not self.api_key:
            raise LLMServiceError(
                "API_KEY is not configured. "
                "Set it in the .env file or environment variables."
            )

        if self.provider == "openai":
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key, timeout=self.timeout_sec)
        elif self.provider == "gemini":
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        else:
            raise LLMServiceError(f"Unsupported LLM provider: {self.provider}")

        return self._client

    def generate(self, prompt: str) -> str:
        # Realiza la inferencia del prompt con reintentos y backoff exponencial
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
                    time.sleep(2 ** attempt)  # Pausa exponencial de 2s, 4s, 8s...

        raise LLMServiceError(
            f"LLM call failed after {self.max_retries} attempts: {last_error}"
        )

    def generate_structured(self, prompt: str) -> tuple[str, dict[str, Any]]:
        # Genera el texto del LLM y lo parsea a un diccionario estructurado
        raw = self.generate(prompt)
        parsed = self._parse_json_response(raw)
        return raw, parsed

    @staticmethod
    def _parse_json_response(raw: str) -> dict[str, Any]:
        # Limpia los delimitadores de código markdown ```json y parsea a JSON
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
