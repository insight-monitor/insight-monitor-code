from pydantic import BaseModel        # Pydantic base model class
from datetime import datetime         # Standard library date and time representation


# Consolidated context of a session used as input for the inference pipeline
class SessionContext(BaseModel):
    session_id: str                          # Unique identifier of the session
    start_time: datetime                     # Date and time when the session started
    end_time: datetime | None = None         # Date and time when the session ended
    duration_seconds: float | None = None    # Calculated total duration in seconds
    app_sequence: list[str] = []             # Chronological sequence of active processes
    event_count: int = 0                     # Total number of events in this session
    screenshot_count: int = 0                # Total number of screenshots in this session
    avg_clicks_per_min: float | None = None  # Average mouse clicks per minute
    avg_keystrokes_per_min: float | None = None # Average keystrokes per minute
    active_apps: list[str] = []              # Set of unique applications used
    status: str = "open"                     # Current state of the session: "open" or "closed"
    session_type: str | None = None          # Inferred session classification type
    goal: str | None = None                  # Inferred session objective description
    confidence: float | None = None          # Model confidence score for the goal classification
