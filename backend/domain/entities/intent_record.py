from typing import Literal            # Standard library type hinting for literal values
from pydantic import BaseModel, Field, ConfigDict # Pydantic types and validators
from datetime import datetime         # Standard library date and time representation

# Supported classification types for session analysis
SessionType = Literal[
    "skill_development",   # Learning a new skill or theoretical concept
    "applied_learning",    # Practical implementation of code or design
    "peer_collaboration",  # Active collaboration with team members or meetings
    "ambiguous",           # Unclear activity or insufficient evidence
    "personal"             # Personal use or entertainment activity
]


# Analytical record representing the inferred intent of a session
class IntentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Enables mapping from database ORM attributes

    record_id: str             # Unique UUID identifier for this analysis record
    session_id: str            # Identifier of the analyzed session
    timestamp: datetime        # UTC date and time of the analysis execution

    session_type: SessionType  # Main classification code of the session
    goal: str                  # Principal objective text inferred by the LLM
    goal_confidence: float = Field(..., ge=0.0, le=1.0)  # Meta confidence level [0-1]

    friction_points: list[str] = []          # List of obstacles or issues detected
    friction_confidence: float | None = None  # Confidence score for the detected friction

    category: str = "ambiguous"              # Specific topic or subcategory tag
    category_confidence: float = Field(default=0.0, ge=0.0, le=1.0)  # Confidence score for subcategory

    tags: list[str] = []          # Keywords representing tools and topics
    evidence: list[str] = []      # Factual items supporting the classification
    alternatives: list[str] = []  # Secondary interpretation options

    app_summary: dict = Field(default_factory=dict)  # Process statistics and switches summary
    raw_timeline_summary: str = ""  # Narrative timeline description of the activity

    raw_llm_response: str | None = None  # Complete raw string response from the LLM
