"""Intent record domain entity representing inferred session analysis."""

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


SessionType = Literal[
    "skill_development",   # Learning a new skill or theoretical concept
    "applied_learning",    # Practical implementation of code or design
    "peer_collaboration",  # Active collaboration with team members or meetings
    "ambiguous",           # Unclear activity or insufficient evidence
    "personal"             # Personal use or entertainment activity
]


class IntentRecord(BaseModel):
    """Analytical record representing the inferred intent of a session."""
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