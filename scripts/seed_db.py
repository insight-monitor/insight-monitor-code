"""
Populate SQLite with sample sessions for dashboard development.

Usage:
    python scripts/seed_db.py
"""

import sqlite3
from datetime import datetime, timedelta
from uuid import uuid4
from pathlib import Path

DB_PATH = Path("./data/insight_monitor.db")


def seed():
    Path("./data").mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration_seconds REAL,
            session_type TEXT,
            goal TEXT,
            confidence REAL,
            status TEXT DEFAULT 'open'
        );

        CREATE TABLE IF NOT EXISTS raw_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            session_id TEXT,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            window_title TEXT,
            process_name TEXT,
            clicks_per_min REAL,
            keystrokes_per_min REAL,
            screenshot_path TEXT,
            url TEXT
        );

        CREATE TABLE IF NOT EXISTS intent_records (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            session_type TEXT NOT NULL,
            goal TEXT,
            confidence REAL,
            friction_points TEXT,
            category TEXT,
            created_at TEXT NOT NULL
        );
    """)

    sessions = [
        {
            "id": str(uuid4()),
            "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=1)).isoformat(),
            "duration_seconds": 3600,
            "session_type": "applied_learning",
            "goal": "Build React component with API integration",
            "confidence": 0.85,
            "status": "closed",
        },
        {
            "id": str(uuid4()),
            "start_time": (datetime.now() - timedelta(minutes=45)).isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "session_type": "peer_collaboration",
            "goal": "Code review and pair programming",
            "confidence": 0.72,
            "status": "open",
        },
    ]

    for s in sessions:
        cursor.execute(
            """INSERT OR REPLACE INTO sessions
               (id, start_time, end_time, duration_seconds, session_type, goal, confidence, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (s["id"], s["start_time"], s["end_time"], s["duration_seconds"],
             s["session_type"], s["goal"], s["confidence"], s["status"]),
        )

    conn.commit()
    conn.close()

    print(f"Seeded {len(sessions)} sessions into {DB_PATH}")


if __name__ == "__main__":
    seed()
