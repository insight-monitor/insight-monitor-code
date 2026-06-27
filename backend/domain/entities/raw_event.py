"""Raw event domain entity and event type enumeration."""

from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class EventType(str, Enum):
    """Enumeration of valid event types captured by the monitor agent."""
    WINDOW_FOCUS = "window_focus"
    SCREENSHOT = "screenshot"
    INPUT_ACTIVITY = "input_activity"
    URL_CONTEXT = "url_context"
    SESSION_BOUNDARY = "session_boundary"


class RawEvent(BaseModel):
    """Immutable raw event captured from the user's environment."""
    event_id: str
    event_type: EventType
    timestamp: datetime
    source: str

    window_title: str | None = None
    process_name: str | None = None
    pid: int | None = None

    screenshot_path: str | None = None
    screenshot_thumbnail: str | None = None

    clicks_per_min: float | None = None
    keystrokes_per_min: float | None = None

    url: str | None = None
    browser_tab_title: str | None = None

    session_id: str | None = None
    session_boundary_type: str | None = None  # "start" | "end"