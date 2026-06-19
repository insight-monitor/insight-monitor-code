import json
from datetime import datetime
from typing import Any

from backend.storage.database import Database


class EventRepository:
    def __init__(self, db: Database):
        self.db = db

    def insert(self, event: dict[str, Any]) -> int:
        self.db.execute(
            """INSERT OR IGNORE INTO raw_events
               (event_id, event_type, timestamp, source, window_title,
                process_name, pid, screenshot_path, screenshot_thumbnail,
                clicks_per_min, keystrokes_per_min, url, browser_tab_title,
                session_id, session_boundary_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event.get("event_id"),
                event.get("event_type"),
                event.get("timestamp"),
                event.get("source", "capture-agent"),
                event.get("window_title"),
                event.get("process_name"),
                event.get("pid"),
                event.get("screenshot_path"),
                event.get("screenshot_thumbnail"),
                event.get("clicks_per_min"),
                event.get("keystrokes_per_min"),
                event.get("url"),
                event.get("browser_tab_title"),
                event.get("session_id"),
                event.get("session_boundary_type"),
            ),
        )
        self.db.commit()
        return self.db.execute("SELECT last_insert_rowid()").fetchone()[0]

    def insert_batch(self, events: list[dict[str, Any]]):
        for event in events:
            self.insert(event)

    def find_by_session(self, session_id: str) -> list[dict]:
        return self.db.fetch_all(
            "SELECT * FROM raw_events WHERE session_id = ? ORDER BY timestamp",
            (session_id,),
        )

    def find_recent(self, limit: int = 50) -> list[dict]:
        return self.db.fetch_all(
            "SELECT * FROM raw_events ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )


class SessionRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(self, session: dict[str, Any]) -> str:
        session_id = session["id"]
        self.db.execute(
            """INSERT INTO sessions
               (id, start_time, end_time, duration_seconds, app_sequence,
                event_count, screenshot_count, avg_clicks_per_min,
                avg_keystrokes_per_min, active_apps, session_type,
                goal, confidence, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                session.get("start_time"),
                session.get("end_time"),
                session.get("duration_seconds"),
                json.dumps(session.get("app_sequence", [])),
                session.get("event_count", 0),
                session.get("screenshot_count", 0),
                session.get("avg_clicks_per_min"),
                session.get("avg_keystrokes_per_min"),
                json.dumps(session.get("active_apps", [])),
                session.get("session_type"),
                session.get("goal"),
                session.get("confidence"),
                session.get("status", "open"),
            ),
        )
        self.db.commit()
        return session_id

    def update(self, session_id: str, updates: dict[str, Any]):
        allowed = {
            "end_time", "duration_seconds", "app_sequence", "event_count",
            "screenshot_count", "avg_clicks_per_min", "avg_keystrokes_per_min",
            "active_apps", "session_type", "goal", "confidence", "status",
        }
        fields = {k: v for k, v in updates.items() if k in allowed}
        if not fields:
            return

        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = [
            json.dumps(v) if isinstance(v, (list, dict)) else v
            for v in fields.values()
        ]
        values.append(session_id)
        self.db.execute(
            f"UPDATE sessions SET {set_clause} WHERE id = ?",
            tuple(values),
        )
        self.db.commit()

    def find_all(self, status: str | None = None, limit: int = 50) -> list[dict]:
        if status:
            return self.db.fetch_all(
                "SELECT * FROM sessions WHERE status = ? ORDER BY start_time DESC LIMIT ?",
                (status, limit),
            )
        return self.db.fetch_all(
            "SELECT * FROM sessions ORDER BY start_time DESC LIMIT ?",
            (limit,),
        )

    def find_by_id(self, session_id: str) -> dict | None:
        return self.db.fetch_one(
            "SELECT * FROM sessions WHERE id = ?", (session_id,),
        )


class IntentRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(self, record: dict[str, Any]) -> str:
        record_id = record["record_id"]
        self.db.execute(
            """INSERT INTO intent_records
               (id, session_id, timestamp, session_type, goal,
                goal_confidence, friction_points, friction_confidence,
                category, category_confidence, tags, evidence,
                alternatives, raw_llm_response)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record_id,
                record["session_id"],
                record.get("timestamp"),
                record.get("session_type"),
                record.get("goal"),
                record.get("goal_confidence", 0.0),
                json.dumps(record.get("friction_points", [])),
                record.get("friction_confidence"),
                record.get("category", "ambiguous"),
                record.get("category_confidence", 0.0),
                json.dumps(record.get("tags", [])),
                json.dumps(record.get("evidence", [])),
                json.dumps(record.get("alternatives", [])),
                record.get("raw_llm_response"),
            ),
        )
        self.db.commit()
        return record_id

    def find_by_session(self, session_id: str) -> dict | None:
        return self.db.fetch_one(
            "SELECT * FROM intent_records WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,),
        )

    def find_all(self, limit: int = 50) -> list[dict]:
        return self.db.fetch_all(
            "SELECT * FROM intent_records ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
