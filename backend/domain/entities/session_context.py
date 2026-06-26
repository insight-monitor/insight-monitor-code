"""Session context domain entity for inference pipeline input.

Exports:
    SessionContext: Consolidated session metadata used as LLM input.
"""

from pydantic import BaseModel
from datetime import datetime


class SessionContext(BaseModel):
    """Consolidated context of a session used as input for the inference pipeline.

    Attributes:
        session_id: Unique identifier of the session.
        start_time: Date and time when the session started.
        end_time: Date and time when the session ended.
        duration_seconds: Calculated total duration in seconds.
        app_sequence: Chronological sequence of active processes.
        event_count: Total number of events in this session.
        screenshot_count: Total number of screenshots in this session.
        avg_clicks_per_min: Average mouse clicks per minute.
        avg_keystrokes_per_min: Average keystrokes per minute.
        active_apps: Set of unique applications used.
        status: Current state of the session: "open" or "closed".
        session_type: Inferred session classification type.
        goal: Inferred session objective description.
        confidence: Model confidence score for the goal classification.
    """

    session_id: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float | None = None
    app_sequence: list[str] = []
    event_count: int = 0
    screenshot_count: int = 0
    avg_clicks_per_min: float | None = None
    avg_keystrokes_per_min: float | None = None
    active_apps: list[str] = []
    status: str = "open"
    session_type: str | None = None
    goal: str | None = None
    confidence: float | None = None