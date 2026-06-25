from fastapi import APIRouter, Depends

from backend.domain.entities.raw_event import RawEvent
from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import EventRepository

router = APIRouter(prefix="/events", tags=["events"])


def get_event_repo() -> EventRepository:
    return EventRepository(Database())


@router.post("")
async def create_event(event: RawEvent, event_repo: EventRepository = Depends(get_event_repo)):
    event_dict = event.model_dump()
    event_dict["timestamp"] = event.timestamp.isoformat()
    event_repo.insert(event_dict)
    return {"status": "ok", "event_id": event.event_id}


@router.post("/batch")
async def create_events_batch(events: list[RawEvent], event_repo: EventRepository = Depends(get_event_repo)):
    for event in events:
        event_dict = event.model_dump()
        event_dict["timestamp"] = event.timestamp.isoformat()
        event_repo.insert(event_dict)
    return {"status": "ok", "count": len(events)}


@router.get("")
async def list_events(limit: int = 50, event_repo: EventRepository = Depends(get_event_repo)):
    events = event_repo.find_recent(limit)
    return {"events": events, "count": len(events)}


@router.get("/session/{session_id}")
async def get_session_events(session_id: str, event_repo: EventRepository = Depends(get_event_repo)):
    events = event_repo.find_by_session(session_id)
    return {"session_id": session_id, "events": events, "count": len(events)}