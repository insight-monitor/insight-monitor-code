"""
domain/entities/raw_event.py
----------------------------
Define la entidad RawEvent: la unidad mínima de información que el sistema
captura del entorno del usuario (foco de ventana, captura de pantalla,
actividad de teclado/ratón, contexto de URL y límites de sesión).

Esta entidad es inmutable en su diseño: sólo representa lo que ocurrió,
no interpreta ni clasifica el comportamiento.
"""

from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class EventType(str, Enum):
    """
    Tipos de eventos que el monitor puede capturar.

    - WINDOW_FOCUS      : La ventana activa cambió (cambio de aplicación o título).
    - SCREENSHOT        : Se tomó una captura de pantalla del escritorio.
    - INPUT_ACTIVITY    : Se registró actividad de teclado o ratón (clics, pulsaciones).
    - URL_CONTEXT       : Se detectó una URL activa en el navegador.
    - SESSION_BOUNDARY  : Marca el inicio o el fin de una sesión de trabajo.
    """
    WINDOW_FOCUS = "window_focus"
    SCREENSHOT = "screenshot"
    INPUT_ACTIVITY = "input_activity"
    URL_CONTEXT = "url_context"
    SESSION_BOUNDARY = "session_boundary"


class RawEvent(BaseModel):
    """
    Representa un evento crudo capturado por el agente de monitoreo.

    Todos los campos opcionales son None cuando el tipo de evento
    no los produce (e.g., clicks_per_min sólo viene en INPUT_ACTIVITY).

    Campos obligatorios
    -------------------
    event_id   : Identificador único del evento (UUID).
    event_type : Categoría del evento (ver EventType).
    timestamp  : Momento exacto en que ocurrió el evento.
    source     : Módulo o agente que generó el evento.

    Campos de foco de ventana (WINDOW_FOCUS)
    ----------------------------------------
    window_title  : Título de la ventana activa.
    process_name  : Nombre del proceso (ej. "code.exe", "chrome.exe").
    pid           : ID de proceso del sistema operativo.

    Campos de captura de pantalla (SCREENSHOT)
    -------------------------------------------
    screenshot_path      : Ruta absoluta al archivo de imagen completa.
    screenshot_thumbnail : Ruta o base64 de la miniatura generada.

    Campos de actividad de entrada (INPUT_ACTIVITY)
    -------------------------------------------------
    clicks_per_min     : Tasa de clics por minuto en la ventana activa.
    keystrokes_per_min : Tasa de pulsaciones de tecla por minuto.

    Campos de contexto de URL (URL_CONTEXT)
    ----------------------------------------
    url               : URL activa detectada en el navegador.
    browser_tab_title : Título de la pestaña del navegador.

    Campos de límite de sesión (SESSION_BOUNDARY)
    -----------------------------------------------
    session_id             : ID de la sesión a la que pertenece este límite.
    session_boundary_type  : "start" o "end" según corresponda.
    """
    event_id: str
    event_type: EventType
    timestamp: datetime
    source: str

    window_title: str | None = None
    process_name: str | None = None
    pid: int | None = None

    screenshot_path: str | None = None
    screenshot_thumbnail: str | None = None

    clicks_per_min: float | None = None
    keystrokes_per_min: float | None = None

    url: str | None = None
    browser_tab_title: str | None = None

    session_id: str | None = None
    session_boundary_type: str | None = None
