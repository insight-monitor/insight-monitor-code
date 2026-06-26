"""
domain/entities/intent_record.py
----------------------------------
Define IntentRecord: el esquema de salida del pipeline de inferencia.

Cuando el LLM analiza una sesión, su respuesta JSON se transforma en un
IntentRecord. Este objeto representa la «intención» del usuario durante
la sesión: qué estaba haciendo, con qué nivel de confianza, qué fricción
experimentó y qué evidencia respalda la clasificación.

Es el artefacto final que se persiste en la base de datos y que otros
módulos (dashboard, analytics, API) consultan.
"""

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# ---------------------------------------------------------------------------
# Tipo literal que restringe los valores válidos de session_type.
# Cualquier valor fuera de esta lista será rechazado por Pydantic en runtime.
# ---------------------------------------------------------------------------
SessionType = Literal[
    "skill_development",   # El usuario está aprendiendo una habilidad nueva (tutoriales, cursos).
    "applied_learning",    # El usuario aplica conocimiento en un proyecto real (código, diseño).
    "peer_collaboration",  # Actividad colaborativa con otras personas (reuniones, pair programming).
    "ambiguous",           # Evidencia insuficiente para clasificar con confianza.
    "personal"             # Actividad personal no relacionada con trabajo o estudio.
]


class IntentRecord(BaseModel):
    """
    Registro de intención inferida para una sesión de trabajo/estudio.

    Este modelo es el resultado final del pipeline de inferencia. Combina
    la clasificación del LLM con metadatos de auditoría (timestamp, record_id)
    y el texto crudo de la respuesta del modelo para trazabilidad.

    Configuración
    -------------
    from_attributes=True permite construir instancias desde ORMs o dicts
    con atributos (compatibilidad con SQLAlchemy / repositories).

    Campos de identidad
    --------------------
    record_id  : UUID único del registro de intención.
    session_id : ID de la sesión a la que pertenece este registro.
    timestamp  : Momento UTC en que se generó el registro.

    Clasificación principal
    ------------------------
    session_type      : Categoría de alto nivel de la sesión (ver SessionType).
    goal              : Descripción en lenguaje natural del objetivo del usuario.
    goal_confidence   : Confianza en el goal [0.0 – 1.0]. Validado por Field.

    Fricción detectada
    -------------------
    friction_points     : Lista de obstáculos observados (cambios frecuentes, errores, etc.).
    friction_confidence : Confianza en la detección de fricción (None si no hay fricción).

    Clasificación secundaria
    -------------------------
    category            : Sub-tipo más específico dentro de session_type (ej. "react_tutorial").
    category_confidence : Confianza en la categoría [0.0 – 1.0].

    Evidencia y contexto
    ---------------------
    tags         : Palabras clave que caracterizan la sesión (herramientas, temas).
    evidence     : Observaciones concretas del LLM que justifican la clasificación.
    alternatives : Interpretaciones alternativas menos probables de la sesión.

    Resumen de actividad
    ---------------------
    app_summary          : Dict con primary_apps, total_context_switches y
                           estimated_typing_intensity (generado por el LLM).
    raw_timeline_summary : Narrativa cronológica breve de la sesión (2-4 frases).

    Trazabilidad
    -------------
    raw_llm_response : Texto crudo devuelto por el LLM antes del parsing JSON.
                       Útil para debug y auditoría.
    """
    model_config = ConfigDict(from_attributes=True)

    record_id: str
    session_id: str
    timestamp: datetime

    session_type: SessionType
    goal: str
    goal_confidence: float = Field(..., ge=0.0, le=1.0)

    friction_points: list[str] = []
    friction_confidence: float | None = None

    category: str = "ambiguous"
    category_confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    tags: list[str] = []
    evidence: list[str] = []
    alternatives: list[str] = []

    app_summary: dict = Field(default_factory=dict)
    raw_timeline_summary: str = ""

    raw_llm_response: str | None = None
