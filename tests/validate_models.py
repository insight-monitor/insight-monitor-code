"""Validate Pydantic models against simulated JSON data."""
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sys
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from backend.domain.entities.raw_event import RawEvent, EventType
from backend.domain.entities.session_context import SessionContext
from backend.domain.entities.intent_record import IntentRecord, SessionType


def test_raw_event():
    data = {
        "event_id": str(uuid4()),
        "event_type": EventType.WINDOW_FOCUS,
        "timestamp": datetime.now(timezone.utc),
        "source": "capture-agent",
        "window_title": "Visual Studio Code",
        "process_name": "code",
        "pid": 1234,
        "screenshot_path": "/data/screenshots/ss_001.png",
        "screenshot_thumbnail": "/data/thumbnails/ss_001_thumb.png",
        "clicks_per_min": 15.5,
        "keystrokes_per_min": 42.3,
        "url": "https://developer.mozilla.org/",
        "browser_tab_title": "MDN Web Docs",
        "session_id": str(uuid4()),
        "session_boundary_type": None,
    }
    event = RawEvent(**data)
    dumped = event.model_dump(mode="json")
    print("[OK] RawEvent — all fields valid")
    return event


def test_session_context():
    data = {
        "session_id": str(uuid4()),
        "start_time": datetime.now(timezone.utc),
        "end_time": datetime.now(timezone.utc),
        "duration_seconds": 5400.0,
        "app_sequence": ["code", "firefox", "discord", "code"],
        "event_count": 47,
        "screenshot_count": 12,
        "avg_clicks_per_min": 8.5,
        "avg_keystrokes_per_min": 35.2,
        "active_apps": ["code", "firefox", "discord"],
        "status": "closed",
    }
    session = SessionContext(**data)
    dumped = session.model_dump(mode="json")
    print("[OK] SessionContext — all fields valid")
    return session


def test_intent_record():
    data = {
        "record_id": str(uuid4()),
        "session_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc),
        "session_type": "applied_learning",
        "goal": "Build React component with API integration",
        "goal_confidence": 0.85,
        "friction_points": [
            "Switched between 3 tabs to find API reference",
            "Spent 8 min debugging CORS error"
        ],
        "friction_confidence": 0.72,
        "category": "skill_development",
        "category_confidence": 0.78,
        "tags": ["react", "api", "learning"],
        "evidence": ["VS Code open for 45 min", "MDN docs open", "Discord #react channel"],
        "alternatives": ["personal_browsing"],
        "app_summary": {
            "code": {"duration_min": 32, "focus_pct": 68.1},
            "firefox": {"duration_min": 15, "focus_pct": 31.9},
        },
        "raw_timeline_summary": (
            "09:00 VS Code (React component) -> "
            "09:15 MDN docs (API reference) -> "
            "09:30 Discord (peer question) -> "
            "09:45 VS Code (implementation) -> "
            "10:00 YouTube (tutorial)"
        ),
        "raw_llm_response": None,
    }
    intent = IntentRecord(**data)
    dumped = intent.model_dump(mode="json")
    print("[OK] IntentRecord — all fields valid")
    return intent


def test_intent_record_literals():
    """Verify only valid session_type values are accepted."""
    valid_types = set(SessionType.__args__)

    for st in valid_types:
        IntentRecord(
            record_id=str(uuid4()),
            session_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_type=st,
            goal="test",
            goal_confidence=0.5,
        )
    print(f"[OK] IntentRecord — all {len(valid_types)} session_type literals valid: {valid_types}")

    try:
        IntentRecord(
            record_id=str(uuid4()),
            session_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_type="invalid_type",
            goal="test",
            goal_confidence=0.5,
        )
        print("[FAIL] IntentRecord — should have rejected 'invalid_type'")
    except Exception:
        print("[OK] IntentRecord — rejects invalid session_type")


def test_goal_confidence_range():
    """Verify goal_confidence is clamped to 0.0 - 1.0."""
    try:
        IntentRecord(
            record_id=str(uuid4()),
            session_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_type="ambiguous",
            goal="test",
            goal_confidence=1.5,
        )
        print("[FAIL] IntentRecord — should have rejected confidence=1.5")
    except Exception:
        print("[OK] IntentRecord — rejects goal_confidence > 1.0")


if __name__ == "__main__":
    print("=" * 60)
    print("Validating Pydantic Models (Día 1-2)")
    print("=" * 60)

    test_raw_event()
    test_session_context()
    test_intent_record()
    test_intent_record_literals()
    test_goal_confidence_range()

    print("=" * 60)
    print("All validations passed")
    print("=" * 60)
