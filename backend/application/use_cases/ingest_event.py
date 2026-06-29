from backend.domain.ports.repositories import IEventRepository
from backend.domain.entities.raw_event import RawEvent


class IngestEventUseCase:
    def __init__(self, event_repo: IEventRepository):
        self.event_repo = event_repo

    def execute(self, event: RawEvent) -> str:
        event_dict = event.model_dump()
        event_dict["timestamp"] = event.timestamp.isoformat()
        self.event_repo.insert(event_dict)
        return event.event_id

    def execute_batch(self, events: list[RawEvent]) -> int:
        for event in events:
            self.execute(event)
        return len(events)

    def list_recent(self, limit: int = 50, offset: int = 0) -> dict:
        """Lists recent events with pagination."""
        events = self.event_repo.find_recent(limit, offset)
        total = self.event_repo.count_all()
        return {"events": events, "count": total, "limit": limit, "offset": offset}

    def list_by_session(self, session_id: str, limit: int = 20, offset: int = 0) -> dict:
        """Lists events for a specific session with pagination."""
        events = self.event_repo.find_by_session_paginated(session_id, limit, offset)
        total = self.event_repo.count_by_session(session_id)
        return {"session_id": session_id, "events": events, "count": total, "limit": limit, "offset": offset}