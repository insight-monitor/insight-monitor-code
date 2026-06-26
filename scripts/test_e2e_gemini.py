#!/usr/bin/env python3
"""
E2E test with real LLM API (OpenAI or Gemini).
Runs the full pipeline: simulated events -> API -> Inference Pipeline -> LLM -> IntentRecord.
"""

import os
import sys
import time
import json
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from backend.config import settings
from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import EventRepository, SessionRepository, IntentRepository
from backend.pipeline.inference_pipeline import InferencePipeline
from backend.pipeline.prompt_builder import PromptBuilder
from backend.services.llm_service import LLMService
from backend.domain.entities.intent_record import IntentRecord

API_URL = os.getenv("API_URL", "http://localhost:8002")

# ===== SCENARIOS =====

def make_event(event_type: str, **kwargs) -> Dict[str, Any]:
    return {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "e2e-test",
        "event_type": event_type,
        **kwargs,
    }


def scenario_riwi_coder() -> List[Dict[str, Any]]:
    """Riwi Coder learning session -> should classify as skill_development or applied_learning."""
    return [
        make_event("window_focus", window_title="Visual Studio Code", process_name="code", pid=1234),
        make_event("window_focus", window_title="MDN Web Docs - Mozilla", process_name="firefox", pid=1235,
                   url="https://developer.mozilla.org/en-US/docs/Web/API"),
        make_event("window_focus", window_title="Visual Studio Code", process_name="code", pid=1234),
        make_event("input_activity", clicks_per_min=2.0, keystrokes_per_min=45.0),
        make_event("window_focus", window_title="Discord - #coder-chat", process_name="discord", pid=1236),
        make_event("window_focus", window_title="React Tutorial - freeCodeCamp", process_name="firefox", pid=1235,
                   url="https://www.youtube.com/watch?v=example"),
        make_event("window_focus", window_title="Visual Studio Code", process_name="code", pid=1234),
        make_event("screenshot", screenshot_path="riwi_coder.png"),
        make_event("input_activity", clicks_per_min=5.0, keystrokes_per_min=60.0),
        make_event("session_boundary", session_boundary_type="close"),
    ]


def scenario_bpo_agent() -> List[Dict[str, Any]]:
    """BPO call center agent -> should classify as applied_learning or similar."""
    return [
        make_event("window_focus", window_title="CRM - Customer Dashboard", process_name="chrome", pid=2234,
                   url="https://crm.company.com/customer/98765"),
        make_event("window_focus", window_title="SAP Business One", process_name="sap", pid=2235),
        make_event("input_activity", clicks_per_min=8.0, keystrokes_per_min=35.0),
        make_event("window_focus", window_title="Softphone - Call 312", process_name="softphone", pid=2236),
        make_event("window_focus", window_title="CRM - Case #44512", process_name="chrome", pid=2234,
                   url="https://crm.company.com/case/44512"),
        make_event("screenshot", screenshot_path="bpo_agent.png"),
        make_event("input_activity", clicks_per_min=12.0, keystrokes_per_min=50.0),
        make_event("session_boundary", session_boundary_type="close"),
    ]


def scenario_mixed() -> List[Dict[str, Any]]:
    """Mixed work + personal -> should classify as personal or ambiguous."""
    return [
        make_event("window_focus", window_title="Visual Studio Code", process_name="code", pid=3234),
        make_event("window_focus", window_title="GitHub - PR #234", process_name="chrome", pid=3235,
                   url="https://github.com/user/repo/pull/234"),
        make_event("input_activity", clicks_per_min=5.0, keystrokes_per_min=40.0),
        make_event("window_focus", window_title="Slack - #dev-team", process_name="slack", pid=3237),
        make_event("window_focus", window_title="YouTube - Music for coding", process_name="chrome", pid=3235,
                   url="https://youtube.com/watch?v=music"),
        make_event("window_focus", window_title="LinkedIn - Feed", process_name="chrome", pid=3235,
                   url="https://linkedin.com/feed"),
        make_event("screenshot", screenshot_path="mixed.png"),
        make_event("window_focus", window_title="Netflix - Series", process_name="chrome", pid=3235,
                   url="https://netflix.com/watch/series"),
        make_event("input_activity", clicks_per_min=2.0, keystrokes_per_min=5.0),
        make_event("session_boundary", session_boundary_type="close"),
    ]


SCENARIOS = {
    "riwi_coder": scenario_riwi_coder,
    "bpo_agent": scenario_bpo_agent,
    "mixed": scenario_mixed,
}

# ===== HELPERS =====

def send_events(events: List[Dict[str, Any]]) -> str:
    """Send events to API (without session_id, let builder assign). Return the session_id assigned by builder."""
    # Remove session_id from events to let builder assign
    for event in events:
        event.pop("session_id", None)
    
    with httpx.Client(timeout=30) as client:
        for event in events:
            try:
                resp = client.post(f"{API_URL}/events", json=event)
                if resp.status_code not in (200, 201):
                    print(f"  [WARN] Failed to send {event['event_type']}: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"  [ERROR] Failed to send {event['event_type']}: {e}")
            time.sleep(0.05)
    
    # Run session builder to assign events and create session
    from backend.pipeline.session_builder import run_session_builder_once
    run_session_builder_once()
    
    # Find the most recently created session (any status)
    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{API_URL}/sessions")
        if resp.status_code == 200:
            sessions = resp.json().get("sessions", [])
            if sessions:
                return sessions[0]["id"]
    return None


def wait_for_session_closed(session_id: str, timeout: int = 15) -> bool:
    """Poll until session is marked closed, running session builder periodically."""
    with httpx.Client(timeout=10) as client:
        for _ in range(timeout * 2):
            try:
                # Run session builder to assign events and update sessions
                from backend.pipeline.session_builder import run_session_builder_once
                run_session_builder_once()
                
                resp = client.get(f"{API_URL}/sessions/{session_id}")
                if resp.status_code == 200:
                    session = resp.json()
                    if session.get("status") == "closed":
                        return True
            except Exception:
                pass
            time.sleep(0.5)
    
    # Explicitly close if still open
    try:
        client.post(f"{API_URL}/sessions/{session_id}/close", timeout=5)
        # Run builder one more time to finalize
        run_session_builder_once()
    except Exception:
        pass
    
    # Final check
    try:
        resp = client.get(f"{API_URL}/sessions/{session_id}")
        if resp.status_code == 200:
            session = resp.json()
            return session.get("status") == "closed"
    except Exception:
        pass
    return False


def run_inference(session_id: str) -> IntentRecord | None:
    """Run the inference pipeline on a session."""
    print(f"  Running inference on session {session_id}...")
    db = Database()
    pipeline = InferencePipeline(db)
    intent = pipeline.process_session(session_id)
    return intent


def print_intent(intent: IntentRecord, label: str):
    print(f"\n  [{label}] IntentRecord:")
    print(f"    session_type: {intent.session_type}")
    print(f"    goal: {intent.goal}")
    print(f"    goal_confidence: {intent.goal_confidence:.2f}")
    print(f"    category: {intent.category} (conf: {intent.category_confidence:.2f})")
    print(f"    friction_points: {intent.friction_points}")
    print(f"    friction_confidence: {intent.friction_confidence}")
    print(f"    tags: {intent.tags}")
    print(f"    evidence: {intent.evidence[:3]}...")
    print(f"    app_summary: {intent.app_summary}")
    print(f"    raw_timeline_summary: {intent.raw_timeline_summary[:80]}...")


def main():
    print("=" * 60)
    print(f"E2E Test - {settings.llm_provider.title()} Inference")
    print("=" * 60)

    if not settings.api_key:
        print(f"[ERROR] API_KEY not configured in backend/.env")
        sys.exit(1)

    print(f"[INFO] Provider: {settings.llm_provider}, Model: {settings.llm_model}")
    print(f"[INFO] API URL: {API_URL}")

    # Initialize DB - clear existing data
    db = Database()
    for table in ("intent_records", "sessions", "raw_events"):
        db.execute(f"DELETE FROM {table}")
    db.commit()

    results = {}

    for name, scenario_fn in SCENARIOS.items():
        print(f"\n{'='*60}")
        print(f"Scenario: {name}")
        print(f"{'='*60}")

        # 1. Generate events
        events = scenario_fn()
        print(f"[INFO] Generated {len(events)} events for {name}")

        # 2. Send to API
        print("[INFO] Sending events to API...")
        session_id = send_events(events)
        if not session_id:
            print("[ERROR] No session_id returned")
            continue
        print(f"[INFO] Session ID: {session_id}")

        # 3. Wait for session to close
        print("[INFO] Waiting for session to close...")
        if not wait_for_session_closed(session_id):
            print("[WARN] Session did not close in time")
        else:
            print("[INFO] Session closed")

        # 4. Run inference
        intent = run_inference(session_id)
        if intent:
            print_intent(intent, name)
            results[name] = intent
        else:
            print("[ERROR] Inference returned None")
            results[name] = None

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, intent in results.items():
        if intent:
            print(f"  {name}: {intent.session_type} (goal_conf={intent.goal_confidence:.2f})")
        else:
            print(f"  {name}: FAILED")

    print(f"\nDone. Check frontend at {API_URL.replace('8000', '5173')}")


if __name__ == "__main__":
    main()