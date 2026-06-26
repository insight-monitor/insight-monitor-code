from pydantic import BaseModel
from datetime import datetime


# Contexto consolidado de una sesión de trabajo/estudio para inferencia
class SessionContext(BaseModel):
    session_id: str                          # ID único de la sesión
    start_time: datetime                     # Fecha y hora de inicio de la sesión
    end_time: datetime | None = None         # Fecha y hora de finalización de la sesión
    duration_seconds: float | None = None    # Duración total de la sesión en segundos
    app_sequence: list[str] = []             # Secuencia ordenada de aplicaciones utilizadas
    event_count: int = 0                     # Total de eventos registrados en la sesión
    screenshot_count: int = 0                # Total de capturas de pantalla tomadas
    avg_clicks_per_min: float | None = None  # Promedio de clics por minuto
    avg_keystrokes_per_min: float | None = None # Promedio de pulsaciones de teclado por minuto
    active_apps: list[str] = []              # Lista de aplicaciones únicas activas
    status: str = "open"                     # Estado actual de la sesión ("open" o "closed")
    session_type: str | None = None          # Tipo de sesión inferido por el LLM
    goal: str | None = None                  # Objetivo principal de la sesión inferido por el LLM
    confidence: float | None = None          # Nivel de confianza asignado por el LLM [0-1]
