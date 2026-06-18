# Capture Agent

The capture agent is Layer 1 of the Insight Monitor architecture. It runs on the user's machine and polls OS APIs to produce `RawEvent` objects.

## Components

| Module | File | Purpose |
|---|---|---|
| Agent | `capture/agent.py` | Main loop: polls every 5s, sends typed events |
| Window tracker | `capture/window_tracker.py` | `xdotool` + `xprop` for window info and browser tab titles |
| Screenshot capture | `capture/screenshot_capture.py` | `mss` screenshots at configurable interval (default 30s) |
| Input monitor | `capture/input_monitor.py` | `pynput` counters for clicks/min and keystrokes/min (no content) |
| Event sender | `capture/event_sender.py` | HTTP client: POST RawEvents to FastAPI backend |

## Current state

Skeleton working, pending real Linux testing and Wayland compatibility.

## Development

See `backend/backend/config.py` for configurable capture parameters. The agent reads `SESSION_INACTIVITY_GAP_MIN` (default 8 min) to determine session boundaries.
