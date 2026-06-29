"""
ARCH-5: InMemory Repositories
In-memory implementations of the repository ports.
Used exclusively in unit tests — no SQLite, no disk, <0.1s per test.
"""

import copy
from typing import Any, List, Optional

from backend.domain.ports.repositories import (
    IEventRepository,
    ISessionRepository,
    IIntentRepository,
    ITicketRepository,
    ICommentRepository,
)


class InMemoryEventRepository(IEventRepository):
    def __init__(self):
        self._store: dict[str, dict] = {}  # event_id -> event dict

    def insert(self, event: dict[str, Any]) -> int:
        eid = event["event_id"]
        if eid not in self._store:
            self._store[eid] = copy.deepcopy(event)
        return len(self._store)

    def insert_batch(self, events: List[dict[str, Any]]) -> None:
        for e in events:
            self.insert(e)

    def find_by_session(self, session_id: str) -> List[dict]:
        return sorted(
            [copy.deepcopy(e) for e in self._store.values() if e.get("session_id") == session_id],
            key=lambda e: e.get("timestamp", ""),
        )

    def find_by_session_paginated(self, session_id: str, limit: int = 20, offset: int = 0) -> List[dict]:
        matches = sorted(
            [copy.deepcopy(e) for e in self._store.values() if e.get("session_id") == session_id],
            key=lambda e: e.get("timestamp", ""),
        )
        return matches[offset:offset + limit]

    def count_by_session(self, session_id: str) -> int:
        return sum(1 for e in self._store.values() if e.get("session_id") == session_id)

    def find_recent(self, limit: int = 50, offset: int = 0) -> List[dict]:
        sorted_events = sorted(self._store.values(), key=lambda e: e.get("timestamp", ""), reverse=True)
        return [copy.deepcopy(e) for e in sorted_events[offset:offset + limit]]

    def count_all(self) -> int:
        return len(self._store)

    def find_unassigned(self) -> List[dict]:
        return sorted(
            [copy.deepcopy(e) for e in self._store.values() if e.get("session_id") is None],
            key=lambda e: e.get("timestamp", ""),
        )

    def assign_to_session(self, event_id: str, session_id: str) -> None:
        if event_id in self._store:
            self._store[event_id]["session_id"] = session_id


class InMemorySessionRepository(ISessionRepository):
    def __init__(self):
        self._store: dict[str, dict] = {}  # session_id -> session dict

    def create(self, session: dict[str, Any]) -> str:
        sid = session["id"]
        self._store[sid] = copy.deepcopy(session)
        return sid

    def update(self, session_id: str, updates: dict[str, Any]) -> None:
        if session_id in self._store:
            self._store[session_id].update(updates)

    def find_all(self, status: Optional[str] = None, limit: int = 50) -> List[dict]:
        results = list(self._store.values())
        if status:
            results = [s for s in results if s.get("status") == status]
        results.sort(key=lambda s: s.get("start_time", ""), reverse=True)
        return [copy.deepcopy(s) for s in results[:limit]]

    def find_by_id(self, session_id: str) -> Optional[dict]:
        session = self._store.get(session_id)
        return copy.deepcopy(session) if session else None


class InMemoryIntentRepository(IIntentRepository):
    def __init__(self):
        self._store: dict[str, dict] = {}  # record_id -> intent dict

    def create(self, record: dict[str, Any]) -> str:
        rid = record["record_id"]
        self._store[rid] = copy.deepcopy(record)
        return rid

    def find_by_session(self, session_id: str) -> Optional[dict]:
        matches = [r for r in self._store.values() if r.get("session_id") == session_id]
        if not matches:
            return None
        return copy.deepcopy(sorted(matches, key=lambda r: r.get("timestamp", ""), reverse=True)[0])

    def find_all(self, limit: int = 50) -> List[dict]:
        sorted_records = sorted(self._store.values(), key=lambda r: r.get("timestamp", ""), reverse=True)
        return [copy.deepcopy(r) for r in sorted_records[:limit]]


class InMemoryTicketRepository(ITicketRepository):
    def __init__(self):
        self._store: dict[str, dict] = {}

    def create(self, ticket: dict[str, Any]) -> str:
        ticket_id = ticket["id"]
        self._store[ticket_id] = copy.deepcopy(ticket)
        return ticket_id

    def find_all(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[dict]:
        results = list(self._store.values())
        if status:
            results = [t for t in results if t.get("status") == status]
        results.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        return [copy.deepcopy(t) for t in results[offset:offset + limit]]

    def count_all(self, status: Optional[str] = None) -> int:
        if status:
            return sum(1 for t in self._store.values() if t.get("status") == status)
        return len(self._store)

    def find_by_id(self, ticket_id: str) -> Optional[dict]:
        ticket = self._store.get(ticket_id)
        return copy.deepcopy(ticket) if ticket else None

    def update(self, ticket_id: str, updates: dict[str, Any]) -> None:
        if ticket_id not in self._store:
            return
        self._store[ticket_id].update(updates)

    def delete(self, ticket_id: str) -> None:
        self._store.pop(ticket_id, None)

    def stat_counts(self) -> dict[str, int]:
        counts = {"total": 0, "open": 0, "in_progress": 0, "resolved": 0, "closed": 0}
        for ticket in self._store.values():
            counts["total"] += 1
            status = ticket.get("status")
            if status in counts:
                counts[status] += 1
        return counts


class InMemoryCommentRepository(ICommentRepository):
    def __init__(self):
        self._store: dict[str, dict] = {}

    def create(self, comment: dict[str, Any]) -> str:
        comment_id = comment["id"]
        self._store[comment_id] = copy.deepcopy(comment)
        return comment_id

    def find_by_ticket(self, ticket_id: str) -> List[dict]:
        comments = [copy.deepcopy(c) for c in self._store.values() if c.get("ticket_id") == ticket_id]
        comments.sort(key=lambda c: c.get("created_at", ""))
        return comments

    def find_by_id(self, comment_id: str) -> Optional[dict]:
        comment = self._store.get(comment_id)
        return copy.deepcopy(comment) if comment else None

    def delete_by_ticket(self, ticket_id: str) -> None:
        to_remove = [cid for cid, c in self._store.items() if c.get("ticket_id") == ticket_id]
        for cid in to_remove:
            self._store.pop(cid, None)
