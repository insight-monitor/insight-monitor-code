from enum import Enum                 # Standard library Enum support
from pydantic import BaseModel        # Pydantic base model class
from datetime import datetime         # Standard library date and time representation


# Enumeration of valid event types captured by the monitor agent
class EventType(str, Enum):
    WINDOW_FOCUS = "window_focus"
    SCREENSHOT = "screenshot"
    INPUT_ACTIVITY = "input_activity"
    URL_CONTEXT = "url_context"
    SESSION_BOUNDARY = "session_boundary"


# Immutable raw event captured from the user's environment
class RawEvent(BaseModel):
    event_id: str                          # Unique identifier of the event (UUID)
    event_type: EventType                  # Classification type of the captured event
    timestamp: datetime                    # UTC timestamp when the event occurred
    source: str                            # Collector module source identifier

    window_title: str | None = None        # Title text of the active focused window
    process_name: str | None = None        # Name of the active process executable (e.g. code.exe)
    pid: int | None = None                 # OS process ID of the active window

    screenshot_path: str | None = None     # Absolute file path to the full screenshot image
    screenshot_thumbnail: str | None = None # File path to the generated thumbnail image

    clicks_per_min: float | None = None    # Clicks rate per minute on input activity
    keystrokes_per_min: float | None = None # Keystrokes rate per minute on input activity

    url: str | None = None                 # Web page address from browser context
    browser_tab_title: str | None = None   # Title text of the active browser tab

    session_id: str | None = None          # Associated logical session ID
    session_boundary_type: str | None = None # Session boundary action type: "start" or "end"
