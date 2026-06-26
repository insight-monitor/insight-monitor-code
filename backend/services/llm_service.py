"""
services/llm_service.py
------------------------
Capa de abstracción sobre los proveedores de LLM (OpenAI y Gemini).

Responsabilidades:
- Inicializar el cliente del proveedor de forma lazy (solo cuando se necesita).
- Ejecutar llamadas al LLM con reintentos y backoff exponencial.
- Parsear la respuesta de texto a dict JSON validado.
- Exponer una interfaz única (generate / generate_structured) independiente
  del proveedor subyacente.

Proveedores soportados:
- "openai"  → usa el SDK oficial openai (ChatCompletion).
- "gemini"  → usa google.genai (models.generate_content).

La configuración (proveedor, modelo, api_key, timeouts, reintentos) se lee
del objeto `settings` (backend.config) y puede sobreescribirse vía constructor
para pruebas o casos especiales.
"""

import json
import logging
import time
from typing import Any

from backend.config import settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """
    Excepción lanzada por LLMService ante fallos irrecuperables.

    Casos de uso:
    - API key no configurada.
    - Proveedor no soportado.
    - Todos los reintentos agotados.
    - Respuesta que no puede parsearse como JSON válido.
    """
    pass


class LLMService:
    """
    Servicio de inferencia LLM con soporte para múltiples proveedores.

    El cliente del proveedor se inicializa de forma lazy en `_get_client`
    para no abrir conexiones antes de que sean necesarias.

    Parámetros del constructor
    --------------------------
    provider    : Nombre del proveedor ("openai" o "gemini").
                  Si None, se usa settings.llm_provider.
    api_key     : API key del proveedor. Si None, se usa settings.api_key.
    model       : Nombre del modelo a usar (ej. "gpt-4o", "gemini-1.5-pro").
                  Si None, se usa settings.llm_model.
    timeout_sec : Tiempo máximo de espera por llamada al LLM en segundos.
                  Si None, se usa settings.inference_timeout_sec.
    max_retries : Número máximo de reintentos ante fallos transitorios.
                  Si None, se usa settings.inference_max_retries.
    """

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
        self._client: Any = None  # Inicializado lazy en _get_client

    def _get_client(self) -> Any:
        """
        Retorna el cliente del proveedor LLM, inicializándolo si es la primera llamada.

        Usa el patrón singleton ligero: si ya existe _client lo retorna directamente.
        En caso contrario, instancia el SDK del proveedor correspondiente.

        Lanza
        -----
        LLMServiceError — Si api_key no está configurada o el proveedor no es válido.
        """
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
        """
        Envía el prompt al LLM y retorna la respuesta en texto plano.

        Implementa reintentos con backoff exponencial (2^attempt segundos)
        para manejar errores transitorios de red o rate limiting.

        Parámetros de inferencia usados para ambos proveedores:
        - max_tokens / max_output_tokens: 2048
        - temperature: 0.2  (respuestas deterministas, baja creatividad)
        - top_p: 0.95

        Parámetros
        ----------
        prompt : Texto completo del prompt a enviar al modelo.

        Retorna
        -------
        str — Texto de la respuesta del LLM.

        Lanza
        -----
        LLMServiceError — Si todos los reintentos fallan.
        """
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
                    time.sleep(2 ** attempt)  # Backoff exponencial: 2s, 4s, 8s…

        raise LLMServiceError(
            f"LLM call failed after {self.max_retries} attempts: {last_error}"
        )

    def generate_structured(self, prompt: str) -> tuple[str, dict[str, Any]]:
        """
        Genera una respuesta y la parsea como JSON estructurado.

        Combina `generate` con `_parse_json_response` para obtener tanto
        el texto crudo (para trazabilidad) como el dict Python validado.

        Parámetros
        ----------
        prompt : Texto del prompt a enviar al modelo.

        Retorna
        -------
        tuple[str, dict] — (texto crudo de la respuesta, dict parseado).

        Lanza
        -----
        LLMServiceError — Si la llamada falla o la respuesta no es JSON válido.
        """
        raw = self.generate(prompt)
        parsed = self._parse_json_response(raw)
        return raw, parsed

    @staticmethod
    def _parse_json_response(raw: str) -> dict[str, Any]:
        """
        Limpia y parsea la respuesta de texto del LLM como JSON.

        Maneja el caso común donde el modelo envuelve el JSON en un
        bloque de código markdown (```json ... ```) a pesar de las
        instrucciones del prompt.

        Parámetros
        ----------
        raw : Texto crudo devuelto por el LLM.

        Retorna
        -------
        dict — El JSON parseado como dict Python.

        Lanza
        -----
        LLMServiceError — Si el texto (limpio) no puede interpretarse como JSON.
        """
        cleaned = raw.strip()
        # Eliminar bloque de código markdown si el modelo lo incluyó
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]  # Quitar el identificador de lenguaje "json"
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise LLMServiceError(
                f"Failed to parse LLM response as JSON: {e}\nRaw response: {raw[:500]}"
            )
