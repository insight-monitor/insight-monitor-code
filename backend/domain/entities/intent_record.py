from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# Tipos de sesión soportados por el clasificador
SessionType = Literal[
    "skill_development",   # Desarrollo de habilidades / aprendizaje teórico
    "applied_learning",    # Aprendizaje aplicado en proyectos prácticos
    "peer_collaboration",  # Colaboración activa con compañeros/reuniones
    "ambiguous",           # Sesión con actividad ambigua o poco clara
    "personal"             # Actividades de uso personal o de ocio
]


# Registro de intención inferida para una sesión
class IntentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Permite instanciar desde objetos tipo ORM

    record_id: str             # Identificador único del registro (UUID)
    session_id: str            # ID de la sesión analizada
    timestamp: datetime        # Fecha y hora UTC de la inferencia

    session_type: SessionType  # Clasificación principal de la sesión
    goal: str                  # Objetivo principal deducido para la sesión
    goal_confidence: float = Field(..., ge=0.0, le=1.0)  # Confianza de la meta [0-1]

    friction_points: list[str] = []          # Puntos de fricción o bloqueos encontrados
    friction_confidence: float | None = None  # Confianza en la fricción (None si no aplica)

    category: str = "ambiguous"              # Categoría específica/tema de la sesión
    category_confidence: float = Field(default=0.0, ge=0.0, le=1.0)  # Confianza en la categoría

    tags: list[str] = []          # Etiquetas asociadas a herramientas o tecnologías
    evidence: list[str] = []      # Observaciones del comportamiento que validan el análisis
    alternatives: list[str] = []  # Hipótesis alternativas de intención

    app_summary: dict = Field(default_factory=dict)  # Resumen de uso de aplicaciones y switches
    raw_timeline_summary: str = ""  # Resumen cronológico en prosa

    raw_llm_response: str | None = None  # Respuesta en texto crudo del LLM para auditoría
