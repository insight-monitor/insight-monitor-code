"""
domain/entities/session_context.py
------------------------------------
Define SessionContext: el esquema de entrada del pipeline de inferencia.

Esta entidad representa el resumen consolidado de una sesión de trabajo,
construido por Person B (session_builder.py). Es el objeto que el pipeline
consume para generar el IntentRecord correspondiente.

No contiene lógica de negocio: es un DTO (Data Transfer Object) de dominio
que agrupa toda la información disponible sobre la sesión antes de invocar al LLM.
"""

from pydantic import BaseModel
from datetime import datetime


class SessionContext(BaseModel):
    """
    Contexto consolidado de una sesión de trabajo/estudio.

    Este modelo actúa como la «vista» de la sesión que el pipeline de
    inferencia necesita: reúne métricas de actividad, secuencia de apps
    y metadatos temporales en un único objeto validado por Pydantic.

    Campos de identidad y tiempo
    -----------------------------
    session_id       : Identificador único de la sesión (UUID).
    start_time       : Marca de tiempo de inicio de la sesión.
    end_time         : Marca de tiempo de cierre (None si la sesión está abierta).
    duration_seconds : Duración total en segundos (calculada por el session_builder).

    Campos de actividad de aplicaciones
    -------------------------------------
    app_sequence  : Lista ordenada de aplicaciones visitadas durante la sesión
                    (incluye repeticiones para reflejar la secuencia real).
    event_count   : Total de eventos registrados en la sesión.
    screenshot_count : Número de capturas de pantalla tomadas.
    active_apps   : Set de aplicaciones únicas activas (sin repetición).

    Campos de actividad de entrada
    --------------------------------
    avg_clicks_per_min     : Promedio de clics por minuto a lo largo de la sesión.
    avg_keystrokes_per_min : Promedio de pulsaciones por minuto a lo largo de la sesión.

    Campos de estado e inferencia
    ------------------------------
    status       : Estado actual de la sesión: "open" (en curso) o "closed" (finalizada).
    session_type : Tipo inferido de la sesión (poblado después de la inferencia, None antes).
    goal         : Objetivo inferido en lenguaje natural (poblado post-inferencia).
    confidence   : Nivel de confianza de la clasificación (0.0 – 1.0, None antes de inferir).
    """
    session_id: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float | None = None
    app_sequence: list[str] = []
    event_count: int = 0
    screenshot_count: int = 0
    avg_clicks_per_min: float | None = None
    avg_keystrokes_per_min: float | None = None
    active_apps: list[str] = []
    status: str = "open"
    session_type: str | None = None
    goal: str | None = None
    confidence: float | None = None
