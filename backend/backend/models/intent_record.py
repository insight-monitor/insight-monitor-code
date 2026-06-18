from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

SessionType = Literal[
    "skill_development",
    "applied_learning",
    "peer_collaboration",
    "ambiguous",
    "personal"
]


class IntentRecord(BaseModel):
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
