"""Raw event domain entity and event type enumeration.

Exports:
    EventType: Enumeration of captured event categories.
    RawEvent: Immutable event record from the monitoring agent.
"""

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
    """Immutable raw event captured from the user's environment.

    Attributes:
        event_id: Unique identifier of the event (UUID).
        event_type: Classification type of the captured event.
        timestamp: UTC timestamp when the event occurred.
        source: Collector module source identifier.
        window_title: Title text of the active focused window.
        process_name: Name of the active process executable (e.g., code.exe).
        pid: OS process ID of the active window.
        screenshot_path: Absolute file path to the full screenshot image.
        screenshot_thumbnail: File path to the generated thumbnail image.
        clicks_per_min: Clicks rate per minute on input activity.
        keystrokes_per_min: Keystrokes rate per minute on input activity.
        url: Web page address from browser context.
        browser_tab_title: Title text of the active browser tab.
        session_id: Associated logical session ID.
        session_boundary_type: Session boundary action type: "start" or "end".
    """

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
    session_boundary_type: str | None = None