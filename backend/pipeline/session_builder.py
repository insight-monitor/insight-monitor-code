import json
import logging
import os
from datetime import datetime, timezone
from uuid import uuid4

from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import EventRepository, SessionRepository

logger = logging.getLogger(__name__)

INACTIVITY_THRESHOLD = int(os.getenv("INACTIVITY_THRESHOLD_MINUTES", "8"))
POLL_INTERVAL = int(os.getenv("SESSION_BUILDER_POLL_SECONDS", "30"))


class SessionBuilder:
    def __init__(self, db: Database):
        self.db = db
        self.event_repo = EventRepository(db)
        self.session_repo = SessionRepository(db)
        self._running = False

    def start(self):
        self._running = True
        logger.info(
            "Session builder started (inactivity_threshold=%dmin, poll=%ds)",
            INACTIVITY_THRESHOLD,
            POLL_INTERVAL,
        )

    def stop(self):
        self._running = False
        logger.info("Session builder stopped")

    def process_pending_events(self):
        unassigned = self.db.fetch_all(
            "SELECT * FROM raw_events WHERE session_id IS NULL ORDER BY timestamp ASC"
        )
        if not unassigned:
            return

        open_sessions = self.db.fetch_all(
            "SELECT * FROM sessions WHERE status = 'open' ORDER BY start_time DESC"
        )

        for event in unassigned:
            candidate = self._find_session_for_event(event, open_sessions)
            if candidate:
                self._assign_event(event, candidate)
                self._update_session_on_event(candidate, event)
            else:
                session_id = self._create_session(event)
                self._assign_event(event, {"id": session_id})
                open_sessions.append(
                    self.session_repo.find_by_id(session_id)
                )

        for session in open_sessions:
            self._check_close(session)

    def _find_session_for_event(
        self, event: dict, open_sessions: list[dict]
    ) -> dict | None:
        event_ts = self._parse_timestamp(event["timestamp"])

        for session in open_sessions:
            session_start = self._parse_timestamp(session["start_time"])
            session_end = session.get("end_time")
            if session_end:
                session_end_ts = self._parse_timestamp(session_end)
            else:
                session_end_ts = event_ts

            if session_start <= event_ts:
                gap = (event_ts - session_end_ts).total_seconds() / 60
                if gap <= INACTIVITY_THRESHOLD:
                    return session

        return None

    def _create_session(self, first_event: dict) -> str:
        session_id = str(uuid4())
        session = {
            "id": session_id,
            "start_time": first_event["timestamp"],
            "end_time": None,
            "duration_seconds": None,
            "app_sequence": [],
            "event_count": 0,
            "screenshot_count": 0,
            "avg_clicks_per_min": None,
            "avg_keystrokes_per_min": None,
            "active_apps": [],
            "session_type": None,
            "goal": None,
            "confidence": None,
            "status": "open",
        }
        self.session_repo.create(session)
        logger.info("Created session %s starting at %s", session_id, first_event["timestamp"])
        return session_id

    def _assign_event(self, event: dict, session: dict):
        self.db.execute(
            "UPDATE raw_events SET session_id = ? WHERE event_id = ?",
            (session["id"], event["event_id"]),
        )
        self.db.commit()

    def _update_session_on_event(self, session: dict, event: dict):
        event_count = (session.get("event_count") or 0) + 1
        screenshot_count = (session.get("screenshot_count") or 0) + (
            1 if event.get("event_type") == "screenshot" else 0
        )
        end_time = event["timestamp"]

        app_seq_raw = session.get("app_sequence", "[]")
        app_sequence = json.loads(app_seq_raw) if isinstance(app_seq_raw, str) else (app_seq_raw or [])
        process = event.get("process_name")
        if process and (not app_sequence or app_sequence[-1] != process):
            app_sequence.append(process)

        active_apps_raw = session.get("active_apps", "[]")
        active_apps = json.loads(active_apps_raw) if isinstance(active_apps_raw, str) else (active_apps_raw or [])
        if process and process not in active_apps:
            active_apps.append(process)

        duration = None
        try:
            start = datetime.fromisoformat(session["start_time"])
            end = datetime.fromisoformat(end_time)
            duration = (end - start).total_seconds()
        except (ValueError, TypeError):
            pass

        updates = {
            "end_time": end_time,
            "duration_seconds": duration,
            "app_sequence": app_sequence,
            "event_count": event_count,
            "screenshot_count": screenshot_count,
            "active_apps": active_apps,
        }

        if event.get("event_type") == "session_boundary" and event.get("session_boundary_type") == "close":
            updates["status"] = "closed"
            logger.info("Session %s closed by boundary event", session["id"])

        self.session_repo.update(session["id"], updates)

    def _check_close(self, session: dict):
        if not session.get("end_time"):
            return

        try:
            last_event = self._parse_timestamp(session["end_time"])
        except (ValueError, TypeError):
            return

        now = datetime.now(timezone.utc)
        gap = (now - last_event).total_seconds() / 60

        if gap > INACTIVITY_THRESHOLD:
            self.session_repo.update(session["id"], {"status": "closed"})
            logger.info(
                "Session %s closed (inactivity gap=%.1fmin > %dmin)",
                session["id"],
                gap,
                INACTIVITY_THRESHOLD,
            )

    def close_session(self, session_id: str):
        session = self.session_repo.find_by_id(session_id)
        if not session:
            logger.warning("Session %s not found for close", session_id)
            return
        if session.get("status") == "closed":
            return
        self.session_repo.update(session_id, {"status": "closed"})
        logger.info("Session %s explicitly closed", session_id)

    @staticmethod
    def _parse_timestamp(ts: str) -> datetime:
        try:
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            return datetime.now(timezone.utc)


def run_session_builder_once():
    db = Database()
    builder = SessionBuilder(db)
    builder.process_pending_events()
