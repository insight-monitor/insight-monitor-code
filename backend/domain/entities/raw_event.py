from enum import Enum
from pydantic import BaseModel
from datetime import datetime


# Tipos de eventos capturados por el monitor de actividad
class EventType(str, Enum):
    WINDOW_FOCUS = "window_focus"
    SCREENSHOT = "screenshot"
    INPUT_ACTIVITY = "input_activity"
    URL_CONTEXT = "url_context"
    SESSION_BOUNDARY = "session_boundary"


# Evento crudo capturado por el agente de monitoreo
class RawEvent(BaseModel):
    event_id: str                          # Identificador único del evento (UUID)
    event_type: EventType                  # Tipo de evento capturado
    timestamp: datetime                    # Fecha y hora UTC del evento
    source: str                            # Módulo origen del evento

    window_title: str | None = None        # Título de la ventana activa
    process_name: str | None = None        # Nombre del proceso ejecutable (ej. code.exe)
    pid: int | None = None                 # ID del proceso del sistema operativo

    screenshot_path: str | None = None     # Ruta a la captura de pantalla completa
    screenshot_thumbnail: str | None = None # Ruta a la miniatura de la captura

    clicks_per_min: float | None = None    # Clics por minuto detectados
    keystrokes_per_min: float | None = None # Pulsaciones de teclado por minuto

    url: str | None = None                 # URL activa del navegador web
    browser_tab_title: str | None = None   # Título de la pestaña activa del navegador

    session_id: str | None = None          # ID de sesión asociado al evento
    session_boundary_type: str | None = None # Tipo de límite: "start" o "end"
