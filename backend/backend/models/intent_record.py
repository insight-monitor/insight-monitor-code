from pydantic import BaseModel
from datetime import datetime


class IntentRecord(BaseModel):
    record_id: str
    session_id: str
    timestamp: datetime

    session_type: str
    goal: str
    goal_confidence: float

    friction_points: list[str] = []
    friction_confidence: float | None = None

    category: str = "ambiguous"
    category_confidence: float = 0.0

    tags: list[str] = []
    evidence: list[str] = []
    alternatives: list[str] = []

    raw_llm_response: str | None = None
