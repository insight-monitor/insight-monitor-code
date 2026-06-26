"""Session context domain entity for inference pipeline input."""

from pydantic import BaseModel
from datetime import datetime


class SessionContext(BaseModel):
    """Consolidated session metadata used as LLM input."""
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
    status: str = "open"  # "open" | "closed"
    session_type: str | None = None
    goal: str | None = None
    confidence: float | None = None