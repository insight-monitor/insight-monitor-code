"""
ARCH-5: Repositorios InMemory
Implementaciones en memoria de los puertos de repositorio.
Usados exclusivamente en tests unitarios — sin SQLite, sin disco, <0.1s por test.
"""

import copy
from typing import Any, List, Optional

from backend.domain.ports.repositories import IEventRepository, ISessionRepository, IIntentRepository


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

    def find_recent(self, limit: int = 50) -> List[dict]:
        sorted_events = sorted(self._store.values(), key=lambda e: e.get("timestamp", ""), reverse=True)
        return [copy.deepcopy(e) for e in sorted_events[:limit]]

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
