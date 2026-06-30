---
title: Data Acquisition
type: reference
domain: data-model
priority: high
status: review
version: 1.0.0
---

# Data Acquisition

## Acquisition mechanisms

### OS-level APIs
Captures active window information, application metadata, and focus events. On Linux this uses `xdotool` and `xprop`. Does not require kernel-level access.

### Screenshot capture
Periodic screen capture at configurable intervals (default 30 seconds). Uses the `mss` library. Captured frames are sent to the LLM for analysis. Raw frames are not persisted beyond the inference call.

### Process metadata
Application name, process ID, window title, foreground/background state. Collected via `xprop`/`xdotool`.

### Browser URL monitoring
Active tab domain and page title extracted from window title heuristics. Full DOM is never collected.

### Input activity monitoring
Click and keystroke *frequency* (clicks/min, keystrokes/min) — not content. Uses `evdev` (preferred, X11 and Wayland) with `pynput` fallback. The Linux user must be in the `input` group for evdev to read `/dev/input/event*`.

## Currently implemented EventTypes

| Event Type | Source | Data captured |
|---|---|---|
| `window_focus` | `window_tracker.py` | window_title, process_name, pid |
| `screenshot` | `screenshot_capture.py` | screenshot_path, screenshot_thumbnail |
| `input_activity` | `input_monitor.py` | clicks_per_min, keystrokes_per_min |
| `url_context` | `window_tracker.py` | url, browser_tab_title |
| `session_boundary` | `agent.py` | session_boundary_type |

## What is NOT acquired
- Keystroke content (individual key presses)
- Clipboard contents
- Microphone or camera input
- File system contents or traversal
- Private browser profiles or incognito windows
- Application memory or internal state
- Credential fields or password manager contents
- Personal communication content without explicit user opt-in
