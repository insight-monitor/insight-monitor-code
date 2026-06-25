"""
Populate SQLite with sample sessions for dashboard development.

Usage:
    python scripts/seed_db.py

Relies on the app's Database._init_schema() to ensure correct table schemas.
Run the backend at least once before seeding, or call Database.get_instance()
which triggers schema creation automatically.
"""

import json
import sys
from datetime import datetime, timedelta
from uuid import uuid4
from pathlib import Path

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import SessionRepository, IntentRepository


DB_PATH = Path("./data/insight_monitor.db")


def seed():
    Path("./data").mkdir(exist_ok=True)

    db = Database(str(DB_PATH))
    session_repo = SessionRepository(db)
    intent_repo = IntentRepository(db)

    now = datetime.now()

    sessions_data = [
        {
            "id": str(uuid4()),
            "start_time": (now - timedelta(hours=2)).isoformat(),
            "end_time": (now - timedelta(hours=1)).isoformat(),
            "duration_seconds": 3600.0,
            "app_sequence": json.dumps(["code", "firefox", "code"]),
            "event_count": 47,
            "screenshot_count": 4,
            "avg_clicks_per_min": 12.5,
            "avg_keystrokes_per_min": 38.2,
            "active_apps": json.dumps(["code", "firefox"]),
            "session_type": "applied_learning",
            "goal": "Build React component with API integration",
            "confidence": 0.85,
            "status": "closed",
        },
        {
            "id": str(uuid4()),
            "start_time": (now - timedelta(minutes=45)).isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "app_sequence": json.dumps(["discord", "code"]),
            "event_count": 23,
            "screenshot_count": 2,
            "avg_clicks_per_min": 8.1,
            "avg_keystrokes_per_min": 22.7,
            "active_apps": json.dumps(["discord", "code"]),
            "session_type": "peer_collaboration",
            "goal": "Code review and pair programming",
            "confidence": 0.72,
            "status": "open",
        },
        {
            "id": str(uuid4()),
            "start_time": (now - timedelta(hours=4)).isoformat(),
            "end_time": (now - timedelta(hours=3, minutes=15)).isoformat(),
            "duration_seconds": 2700.0,
            "app_sequence": json.dumps(["firefox", "chrome", "firefox"]),
            "event_count": 31,
            "screenshot_count": 3,
            "avg_clicks_per_min": 5.3,
            "avg_keystrokes_per_min": 10.1,
            "active_apps": json.dumps(["firefox", "chrome"]),
            "session_type": "research",
            "goal": "Research API documentation for authentication",
            "confidence": 0.65,
            "status": "closed",
        },
    ]

    for s in sessions_data:
        session_repo.create(s)

    intents_data = [
        {
            "record_id": str(uuid4()),
            "session_id": sessions_data[0]["id"],
            "timestamp": now.isoformat(),
            "session_type": "applied_learning",
            "goal": "Build React component with API integration",
            "goal_confidence": 0.85,
            "friction_points": json.dumps(["Switched between 3 tabs to find API reference"]),
            "friction_confidence": 0.6,
            "category": "skill_development",
            "category_confidence": 0.78,
            "tags": json.dumps(["react", "api", "typescript"]),
            "evidence": json.dumps(["VS Code open", "MDN docs open"]),
            "alternatives": json.dumps([]),
            "raw_llm_response": None,
        },
    ]

    for rec in intents_data:
        intent_repo.create(rec)

    print(f"Seeded {len(sessions_data)} sessions and {len(intents_data)} intent records into {DB_PATH}")


if __name__ == "__main__":
    seed()
