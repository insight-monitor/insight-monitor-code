import sqlite3
import threading
from pathlib import Path
from typing import Any

from backend.config import settings


class Database:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._local = threading.local()
        self._init_schema()


    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA foreign_keys=ON")
        return self._local.conn

    def _init_schema(self):
        conn = self._get_connection()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS raw_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'capture-agent',
                window_title TEXT,
                process_name TEXT,
                pid INTEGER,
                screenshot_path TEXT,
                screenshot_thumbnail TEXT,
                clicks_per_min REAL,
                keystrokes_per_min REAL,
                url TEXT,
                browser_tab_title TEXT,
                session_id TEXT,
                session_boundary_type TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_events_session
                ON raw_events(session_id);
            CREATE INDEX IF NOT EXISTS idx_events_timestamp
                ON raw_events(timestamp);

            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds REAL,
                app_sequence TEXT DEFAULT '[]',
                event_count INTEGER DEFAULT 0,
                screenshot_count INTEGER DEFAULT 0,
                avg_clicks_per_min REAL,
                avg_keystrokes_per_min REAL,
                active_apps TEXT DEFAULT '[]',
                session_type TEXT,
                goal TEXT,
                confidence REAL,
                status TEXT DEFAULT 'open',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_status
                ON sessions(status);

            CREATE TABLE IF NOT EXISTS intent_records (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                session_type TEXT NOT NULL,
                goal TEXT,
                goal_confidence REAL DEFAULT 0.0,
                friction_points TEXT DEFAULT '[]',
                friction_confidence REAL,
                category TEXT DEFAULT 'ambiguous',
                category_confidence REAL DEFAULT 0.0,
                tags TEXT DEFAULT '[]',
                evidence TEXT DEFAULT '[]',
                alternatives TEXT DEFAULT '[]',
                app_summary TEXT DEFAULT '{}',
                raw_timeline_summary TEXT DEFAULT '',
                raw_llm_response TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );

            CREATE INDEX IF NOT EXISTS idx_intent_session
                ON intent_records(session_id);

            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT DEFAULT 'open',
                priority TEXT DEFAULT 'medium',
                created_by TEXT DEFAULT 'system',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_tickets_status
                ON tickets(status);

            CREATE TABLE IF NOT EXISTS ticket_comments (
                id TEXT PRIMARY KEY,
                ticket_id TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT DEFAULT 'system',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_comments_ticket
                ON ticket_comments(ticket_id);
        """)
        conn.commit()
        self._migrate()

    def _migrate(self):
        conn = self._get_connection()
        migrations: list[tuple[str, Any]] = [
            (
                "ALTER TABLE intent_records ADD COLUMN app_summary TEXT DEFAULT '{}'",
                "app_summary",
            ),
            (
                "ALTER TABLE intent_records ADD COLUMN raw_timeline_summary TEXT DEFAULT ''",
                "raw_timeline_summary",
            ),
            (
                """CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT DEFAULT 'open',
                    priority TEXT DEFAULT 'medium',
                    created_by TEXT DEFAULT 'system',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )""",
                "tickets",
            ),
            (
                """CREATE TABLE IF NOT EXISTS ticket_comments (
                    id TEXT PRIMARY KEY,
                    ticket_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT DEFAULT 'system',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
                )""",
                "ticket_comments",
            ),
        ]
        for sql, col_name in migrations:
            try:
                conn.execute(sql)
                conn.commit()
            except sqlite3.OperationalError:
                pass

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = self._get_connection()
        return conn.execute(sql, params)

    def execute_many(self, sql: str, params_list: list[tuple]):
        conn = self._get_connection()
        conn.executemany(sql, params_list)
        conn.commit()

    def fetch_one(self, sql: str, params: tuple = ()) -> dict | None:
        cursor = self.execute(sql, params)
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetch_all(self, sql: str, params: tuple = ()) -> list[dict]:
        cursor = self.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def commit(self):
        conn = self._get_connection()
        conn.commit()

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

