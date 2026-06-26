"""Intent record domain entity representing inferred session analysis.

Exports:
    SessionType: Literal type for session classification categories.
    IntentRecord: Structured analysis output from the LLM pipeline.
"""

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
    """Analytical record representing the inferred intent of a session.

    Attributes:
        record_id: Unique UUID identifier for this analysis record.
        session_id: Identifier of the analyzed session.
        timestamp: UTC date and time of the analysis execution.
        session_type: Main classification code of the session.
        goal: Principal objective text inferred by the LLM.
        goal_confidence: Meta confidence level [0-1].
        friction_points: List of obstacles or issues detected.
        friction_confidence: Confidence score for the detected friction.
        category: Specific topic or subcategory tag.
        category_confidence: Confidence score for subcategory.
        tags: Keywords representing tools and topics.
        evidence: Factual items supporting the classification.
        alternatives: Secondary interpretation options.
        app_summary: Process statistics and switches summary.
        raw_timeline_summary: Narrative timeline description of the activity.
        raw_llm_response: Complete raw string response from the LLM.
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