"""
ARCH-4: Use Case — BuildSessions
Orchestrates the logic of grouping unassigned events into work sessions.
Only depends on ports (IEventRepository, ISessionRepository); never SQLite directly.
"""

import json
import logging
import os
from datetime import datetime, timezone
from uuid import uuid4

from backend.domain.ports.repositories import IEventRepository, ISessionRepository

logger = logging.getLogger(__name__)

INACTIVITY_THRESHOLD = int(os.getenv("INACTIVITY_THRESHOLD_MINUTES", "8"))


class BuildSessionsUseCase:
    def __init__(self, event_repo: IEventRepository, session_repo: ISessionRepository):
        self.event_repo = event_repo
        self.session_repo = session_repo

    def execute(self) -> int:
        """
        Processes all unassigned events and groups them into sessions.
        Always runs the inactivity check, even if no new events arrived,
        so idle sessions still transition to status == "closed".
        Returns the number of sessions created or updated.
        """
        sessions_touched = 0
        unassigned = self.event_repo.find_unassigned()

        if unassigned:
            open_sessions = self.session_repo.find_all(status="open")
            for event in unassigned:
                candidate = self._find_session_for_event(event, open_sessions)
                if candidate:
                    self._assign_event_to_session(event, candidate)
                    self._update_session_stats(candidate, event)
                    sessions_touched += 1
                else:
                    new_session_id = self._create_new_session(event)
                    self._assign_event_to_session(event, {"id": new_session_id})
                    new_session = self.session_repo.find_by_id(new_session_id)
                    if new_session:
                        open_sessions.append(new_session)
                    sessions_touched += 1

        # Always re-fetch the open sessions before the inactivity sweep so
        # that we don't miss sessions that have been idle for cycles when no
        # new events arrived. This is the fix for #91: previously, the
        # closing loop only ran inside the `if unassigned` branch, so
        # sessions whose last event was more than the threshold ago never
        # transitioned to status == "closed" until something new arrived.
        self.auto_close_inactive_sessions()

        return sessions_touched

    # ─────────────────────────── inactivity sweep ──────────────────────

    def auto_close_inactive_sessions(self) -> int:
        """Close every open session whose last activity is older than the threshold.

        Returns the number of sessions whose status was changed to "closed".
        Safe to call repeatedly (idempotent). A fresh repo read is done each
        call so we never operate on a stale in-memory list.
        """
        now = datetime.now(timezone.utc)
        threshold_min = INACTIVITY_THRESHOLD
        closed_count = 0

        for session in self.session_repo.find_all(status="open"):
            # Only consider sessions that have actually started.
            last_activity_str = session.get("end_time") or session.get("start_time")
            if not last_activity_str:
                continue
            try:
                last_activity = datetime.fromisoformat(last_activity_str)
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                logger.warning(
                    "Session %s has malformed timestamp %s; skipping",
                    session.get("id"),
                    last_activity_str,
                )
                continue

            gap_min = (now - last_activity).total_seconds() / 60
            if gap_min > threshold_min:
                self.session_repo.update(session["id"], {"status": "closed"})
                logger.info(
                    "Session %s auto-closed (gap=%.1fmin > threshold=%dmin)",
                    session["id"],
                    gap_min,
                    threshold_min,
                )
                closed_count += 1

        return closed_count

    # ─────────────────────────── private helpers ────────────────────────

    def _find_session_for_event(self, event: dict, open_sessions: list[dict]) -> dict | None:
        event_ts = self._parse_ts(event["timestamp"])
        for session in open_sessions:
            start = self._parse_ts(session["start_time"])
            end_raw = session.get("end_time")
            end = self._parse_ts(end_raw) if end_raw else event_ts
            if start <= event_ts:
                gap_min = (event_ts - end).total_seconds() / 60
                if gap_min <= INACTIVITY_THRESHOLD:
                    return session
        return None

    def _create_new_session(self, first_event: dict) -> str:
        session_id = str(uuid4())
        self.session_repo.create({
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
        })
        logger.info("Created session %s at %s", session_id, first_event["timestamp"])
        return session_id

    def _assign_event_to_session(self, event: dict, session: dict):
        """Delegates assignment to the event repository."""
        self.event_repo.assign_to_session(event["event_id"], session["id"])

    def _update_session_stats(self, session: dict, event: dict):
        event_count = (session.get("event_count") or 0) + 1
        screenshot_count = (session.get("screenshot_count") or 0) + (
            1 if event.get("event_type") == "screenshot" else 0
        )
        end_time = event["timestamp"]

        raw_seq = session.get("app_sequence", "[]")
        app_sequence = raw_seq if isinstance(raw_seq, list) else json.loads(raw_seq)
        process = event.get("process_name")
        if process and (not app_sequence or app_sequence[-1] != process):
            app_sequence.append(process)

        raw_apps = session.get("active_apps", "[]")
        active_apps = raw_apps if isinstance(raw_apps, list) else json.loads(raw_apps)
        if process and process not in active_apps:
            active_apps.append(process)

        duration = None
        try:
            start = datetime.fromisoformat(session["start_time"])
            end = datetime.fromisoformat(end_time)
            duration = (end - start).total_seconds()
        except (ValueError, TypeError):
            pass

        status = session.get("status", "open")
        if event.get("event_type") == "session_boundary" and event.get("session_boundary_type") == "close":
            status = "closed"
            logger.info("Session %s explicitly closed by boundary event", session["id"])

        self.session_repo.update(session["id"], {
            "end_time": end_time,
            "duration_seconds": duration,
            "app_sequence": app_sequence,
            "event_count": event_count,
            "screenshot_count": screenshot_count,
            "active_apps": active_apps,
            "status": status,
        })
        # Update in-memory dict so the loop iteration stays coherent
        session.update({"end_time": end_time, "event_count": event_count, "status": status})

    @staticmethod
    def _parse_ts(ts: str) -> datetime:
        try:
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            return datetime.now(timezone.utc)
