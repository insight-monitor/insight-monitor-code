"""
Simulate realistic BPO and Riwi sessions for frontend development.

Usage:
    python scripts/simulate_session.py
"""

import json
import time
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from typing import Any

import httpx

API_URL = "http://localhost:8002"


def make_event(event_type: str, **kwargs) -> dict[str, Any]:
    return {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "simulator",
        "event_type": event_type,
        **kwargs,
    }


def simulate_riwi_coder():
    """Simulate a Riwi Coder learning session."""
    events = [
        make_event("window_focus", window_title="Visual Studio Code", process_name="code",
                   pid=1234),
        make_event("window_focus", window_title="MDN Web Docs - Mozilla", process_name="firefox",
                   pid=1235, url="https://developer.mozilla.org/en-US/docs/Web/API"),
        make_event("window_focus", window_title="Visual Studio Code", process_name="code",
                   pid=1234),
        make_event("input_activity", clicks_per_min=2.0, keystrokes_per_min=45.0),
        make_event("window_focus", window_title="Discord - #coder-chat", process_name="discord",
                   pid=1236),
        make_event("window_focus", window_title="React Tutorial - freeCodeCamp",
                   process_name="firefox", pid=1235,
                   url="https://www.youtube.com/watch?v=example"),
        make_event("window_focus", window_title="Visual Studio Code", process_name="code",
                   pid=1234),
        make_event("screenshot", screenshot_path="simulated_riwi_session.png"),
        make_event("input_activity", clicks_per_min=5.0, keystrokes_per_min=60.0),
        make_event("session_boundary", session_boundary_type="close"),
    ]
    return events


def simulate_bpo_agent():
    """Simulate a BPO call center agent session."""
    events = [
        make_event("window_focus", window_title="CRM - Customer Dashboard",
                   process_name="chrome", pid=2234,
                   url="https://crm.company.com/customer/98765"),
        make_event("window_focus", window_title="SAP Business One", process_name="sap",
                   pid=2235),
        make_event("input_activity", clicks_per_min=8.0, keystrokes_per_min=35.0),
        make_event("window_focus", window_title="Softphone - Call 312", process_name="softphone",
                   pid=2236),
        make_event("window_focus", window_title="CRM - Case #44512", process_name="chrome",
                   pid=2234,
                   url="https://crm.company.com/case/44512"),
        make_event("screenshot", screenshot_path="simulated_bpo_session.png"),
        make_event("input_activity", clicks_per_min=12.0, keystrokes_per_min=50.0),
        make_event("session_boundary", session_boundary_type="close"),
    ]
    return events


def simulate_mixed():
    """Simulate a mixed work + personal session."""
    events = [
        make_event("window_focus", window_title="Visual Studio Code", process_name="code",
                   pid=3234),
        make_event("window_focus", window_title="GitHub - PR #234", process_name="chrome",
                   pid=3235, url="https://github.com/user/repo/pull/234"),
        make_event("input_activity", clicks_per_min=5.0, keystrokes_per_min=40.0),
        make_event("window_focus", window_title="Slack - #dev-team", process_name="slack",
                   pid=3237),
        make_event("window_focus", window_title="YouTube - Music for coding", process_name="chrome",
                   pid=3235, url="https://youtube.com/watch?v=music"),
        make_event("window_focus", window_title="LinkedIn - Feed", process_name="chrome",
                   pid=3235, url="https://linkedin.com/feed"),
        make_event("screenshot", screenshot_path="simulated_mixed_session.png"),
        make_event("window_focus", window_title="Netflix - Series", process_name="chrome",
                   pid=3235, url="https://netflix.com/watch/series"),
        make_event("input_activity", clicks_per_min=2.0, keystrokes_per_min=5.0),
        make_event("session_boundary", session_boundary_type="close"),
    ]
    return events


def send_events(events: list[dict[str, Any]]):
    with httpx.Client(timeout=10) as client:
        for event in events:
            try:
                resp = client.post(f"{API_URL}/events", json=event)
                print(f"  Sent {event['event_type']}: {resp.status_code}")
            except Exception as e:
                print(f"  Failed: {e}")
            time.sleep(0.1)


if __name__ == "__main__":
    print("Simulating Riwi Coder session...")
    send_events(simulate_riwi_coder())

    print("\nSimulating BPO Agent session...")
    send_events(simulate_bpo_agent())

    print("\nSimulating Mixed Work + Personal session...")
    send_events(simulate_mixed())

    print("\nDone. Check the frontend.")
