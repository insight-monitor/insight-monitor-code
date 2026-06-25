# ADR-0004: Capture Agent in Python

## Status

Accepted

## Context

The capture agent needs to poll OS-level APIs for window focus, screenshots, input frequency, and browser context. Options included Python, Rust (performance), Electron (cross-platform UI), and shell scripts (simplicity).

## Decision

Implement the capture agent in Python 3.11+. Python has the best ecosystem for OS-level hooks (`xdotool`, `pynput`, `mss`) and allows code reuse with the backend (same models, same serialization). The agent communicates with the backend via HTTP, allowing independent deployment.

## Consequences

- **Positive**: Reuses Pydantic models; same event format for capture agent and API
- **Positive**: Rich ecosystem for OS interaction (xdotool, pynput, mss, pywin32)
- **Positive**: Faster development than Rust; more maintainable than shell scripts
- **Negative**: Python runtime dependency on the monitored machine
- **Negative**: Higher memory footprint than a compiled language
- **Negative**: Limited to platforms with Python support (Linux MVP, Windows post-MVP)
