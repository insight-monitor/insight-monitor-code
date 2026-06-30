# Capture Agent

The capture agent is Layer 1 of the Insight Monitor architecture. It runs on the user's machine and polls OS APIs to produce `RawEvent` objects.

## Components

| Module | File | Purpose |
|---|---|---|
| Agent | `capture/agent.py` | Main loop: polls every 5s, sends typed events |
| Window tracker | `capture/window_tracker.py` | `xdotool` + `xprop` for window info and browser tab titles |
| Screenshot capture | `capture/screenshot_capture.py` | `mss` screenshots at configurable interval (default 30s) |
| Input monitor | `capture/input_monitor.py` | `evdev` counters for clicks/min and keystrokes/min (no content); falls back to `pynput` if evdev is unavailable. The Linux user must be in the `input` group. |
| Event sender | `capture/event_sender.py` | HTTP client: POST RawEvents to FastAPI backend |

## Resilience (ARCH-8)

The `capture/event_sender.py` now includes:
- **Local buffer** (up to 500 events) when the backend is unreachable
- **Exponential backoff** retries (1s → 2s → 4s) on network errors
- **Auto-flush** on reconnect: buffered events are sent as soon as the API comes back online
- **Graceful shutdown**: flushes the buffer before closing
- HTTP 4xx errors are not retried (client errors); only network errors trigger retries

## Current state

All components implemented. The capture agent survives backend restarts without data loss. **Wayland support implemented** via GNOME Shell extension (GNOME 45+) with `WaylandWindowTracker` polling `/tmp/insight-window.json`. X11 (`xdotool`/`xprop`) and Wayland both supported with auto-detection via `XDG_SESSION_TYPE`.

## Development

See `backend/config.py` for configurable capture parameters. The agent reads `SESSION_INACTIVITY_GAP_MIN` (default 8 min) to determine session boundaries.
