from fastapi import APIRouter, Depends
from backend.domain.entities.raw_event import RawEvent
from backend.application.use_cases.ingest_event import IngestEventUseCase
from backend.infrastructure.di import get_ingest_event_use_case, get_event_repository
from backend.domain.ports.repositories import IEventRepository

router = APIRouter(prefix="/events", tags=["events"])


@router.post("")
async def create_event(
    event: RawEvent, 
    use_case: IngestEventUseCase = Depends(get_ingest_event_use_case)
):
    event_id = use_case.execute(event)
    return {"status": "ok", "event_id": event_id}


@router.post("/batch")
async def create_events_batch(
    events: list[RawEvent],
    use_case: IngestEventUseCase = Depends(get_ingest_event_use_case)
):
    count = use_case.execute_batch(events)
    return {"status": "ok", "count": count}


@router.get("")
async def list_events(
    limit: int = 50,
    repo: IEventRepository = Depends(get_event_repository)
):
    events = repo.find_recent(limit)
    return {"events": events, "count": len(events)}


@router.get("/session/{session_id}")
async def get_session_events(
    session_id: str,
    repo: IEventRepository = Depends(get_event_repository)
):
    events = repo.find_by_session(session_id)
    return {"session_id": session_id, "events": events, "count": len(events)}