import json
from typing import Any

from backend.infrastructure.db.sqlite.database import Database
from backend.domain.ports.repositories import (
    IEventRepository,
    ISessionRepository,
    IIntentRepository,
    ITicketRepository,
    ICommentRepository,
)


def _parse_json_fields(row: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    for field in fields:
        val = row.get(field)
        if isinstance(val, str):
            try:
                row[field] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return row


_SESSION_JSON_FIELDS = ["app_sequence", "active_apps"]
_INTENT_JSON_FIELDS = [
    "friction_points", "tags", "evidence", "alternatives", "app_summary",
]


class EventRepository(IEventRepository):
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

    def find_by_session_paginated(self, session_id: str, limit: int = 20, offset: int = 0) -> list[dict]:
        return self.db.fetch_all(
            "SELECT * FROM raw_events WHERE session_id = ? ORDER BY timestamp LIMIT ? OFFSET ?",
            (session_id, limit, offset),
        )

    def count_by_session(self, session_id: str) -> int:
        row = self.db.fetch_one(
            "SELECT COUNT(*) as cnt FROM raw_events WHERE session_id = ?",
            (session_id,),
        )
        return row["cnt"] if row else 0

    def find_recent(self, limit: int = 50, offset: int = 0) -> list[dict]:
        return self.db.fetch_all(
            "SELECT * FROM raw_events ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )

    def count_all(self) -> int:
        row = self.db.fetch_one("SELECT COUNT(*) as cnt FROM raw_events")
        return row["cnt"] if row else 0

    def find_unassigned(self) -> list[dict]:
        return self.db.fetch_all(
            "SELECT * FROM raw_events WHERE session_id IS NULL ORDER BY timestamp ASC"
        )

    def assign_to_session(self, event_id: str, session_id: str) -> None:
        self.db.execute(
            "UPDATE raw_events SET session_id = ? WHERE event_id = ?",
            (session_id, event_id),
        )
        self.db.commit()


class SessionRepository(ISessionRepository):
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
            rows = self.db.fetch_all(
                "SELECT * FROM sessions WHERE status = ? ORDER BY start_time DESC LIMIT ?",
                (status, limit),
            )
        else:
            rows = self.db.fetch_all(
                "SELECT * FROM sessions ORDER BY start_time DESC LIMIT ?",
                (limit,),
            )
        return [_parse_json_fields(r, _SESSION_JSON_FIELDS) for r in rows]

    def find_by_id(self, session_id: str) -> dict | None:
        row = self.db.fetch_one(
            "SELECT * FROM sessions WHERE id = ?", (session_id,),
        )
        if row:
            row = _parse_json_fields(row, _SESSION_JSON_FIELDS)
        return row


class IntentRepository(IIntentRepository):
    def __init__(self, db: Database):
        self.db = db

    def create(self, record: dict[str, Any]) -> str:
        record_id = record["record_id"]
        self.db.execute(
            """INSERT INTO intent_records
               (id, session_id, timestamp, session_type, goal,
                goal_confidence, friction_points, friction_confidence,
                category, category_confidence, tags, evidence,
                alternatives, app_summary, raw_timeline_summary, raw_llm_response)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                json.dumps(record.get("app_summary", {})),
                record.get("raw_timeline_summary", ""),
                record.get("raw_llm_response"),
            ),
        )
        self.db.commit()
        return record_id

    def find_by_session(self, session_id: str) -> dict | None:
        row = self.db.fetch_one(
            "SELECT * FROM intent_records WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,),
        )
        if row:
            row = _parse_json_fields(row, _INTENT_JSON_FIELDS)
            row["record_id"] = row.pop("id")
        return row

    def find_all(self, limit: int = 50) -> list[dict]:
        rows = self.db.fetch_all(
            "SELECT * FROM intent_records ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        result = []
        for r in rows:
            r = _parse_json_fields(r, _INTENT_JSON_FIELDS)
            r["record_id"] = r.pop("id")
            result.append(r)
        return result


class TicketRepository(ITicketRepository):
    _ALLOWED_UPDATE_FIELDS = {"title", "description", "status", "priority"}

    def __init__(self, db: Database):
        self.db = db

    def create(self, ticket: dict[str, Any]) -> str:
        ticket_id = ticket["id"]
        self.db.execute(
            """INSERT INTO tickets
               (id, title, description, status, priority, created_by, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ticket_id,
                ticket.get("title"),
                ticket.get("description", ""),
                ticket.get("status", "open"),
                ticket.get("priority", "medium"),
                ticket.get("created_by", "system"),
                ticket.get("created_at"),
                ticket.get("updated_at"),
            ),
        )
        self.db.commit()
        return ticket_id

    def find_all(self, status: str | None = None, limit: int = 50, offset: int = 0) -> list[dict]:
        if status:
            return self.db.fetch_all(
                "SELECT * FROM tickets WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (status, limit, offset),
            )
        return self.db.fetch_all(
            "SELECT * FROM tickets ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )

    def count_all(self, status: str | None = None) -> int:
        if status:
            row = self.db.fetch_one(
                "SELECT COUNT(*) as cnt FROM tickets WHERE status = ?", (status,),
            )
        else:
            row = self.db.fetch_one("SELECT COUNT(*) as cnt FROM tickets")
        return row["cnt"] if row else 0

    def find_by_id(self, ticket_id: str) -> dict | None:
        return self.db.fetch_one(
            "SELECT * FROM tickets WHERE id = ?", (ticket_id,),
        )

    def update(self, ticket_id: str, updates: dict[str, Any]) -> None:
        fields = {k: v for k, v in updates.items() if k in self._ALLOWED_UPDATE_FIELDS}
        if not fields:
            return
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [ticket_id]
        self.db.execute(
            f"UPDATE tickets SET {set_clause} WHERE id = ?",
            tuple(values),
        )
        self.db.commit()

    def delete(self, ticket_id: str) -> None:
        self.db.execute(
            "DELETE FROM ticket_comments WHERE ticket_id = ?", (ticket_id,),
        )
        self.db.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        self.db.commit()

    def stat_counts(self) -> dict[str, int]:
        row = self.db.fetch_one("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed
            FROM tickets
        """)
        if not row:
            return {"total": 0, "open": 0, "in_progress": 0, "resolved": 0, "closed": 0}
        return {
            "total": row["total"] or 0,
            "open": row["open"] or 0,
            "in_progress": row["in_progress"] or 0,
            "resolved": row["resolved"] or 0,
            "closed": row["closed"] or 0,
        }


class CommentRepository(ICommentRepository):
    def __init__(self, db: Database):
        self.db = db

    def create(self, comment: dict[str, Any]) -> str:
        comment_id = comment["id"]
        self.db.execute(
            """INSERT INTO ticket_comments
               (id, ticket_id, content, author, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                comment_id,
                comment["ticket_id"],
                comment.get("content"),
                comment.get("author", "system"),
                comment.get("created_at"),
            ),
        )
        self.db.commit()
        return comment_id

    def find_by_ticket(self, ticket_id: str) -> list[dict]:
        return self.db.fetch_all(
            "SELECT * FROM ticket_comments WHERE ticket_id = ? ORDER BY created_at ASC",
            (ticket_id,),
        )

    def find_by_id(self, comment_id: str) -> dict | None:
        return self.db.fetch_one(
            "SELECT * FROM ticket_comments WHERE id = ?", (comment_id,),
        )

    def delete_by_ticket(self, ticket_id: str) -> None:
        self.db.execute(
            "DELETE FROM ticket_comments WHERE ticket_id = ?", (ticket_id,),
        )
        self.db.commit()
