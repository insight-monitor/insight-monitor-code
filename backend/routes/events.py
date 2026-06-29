from fastapi import APIRouter, Depends, Query
from backend.domain.entities.raw_event import RawEvent
from backend.application.use_cases.ingest_event import IngestEventUseCase
from backend.infrastructure.di import get_ingest_event_use_case

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
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    use_case: IngestEventUseCase = Depends(get_ingest_event_use_case)
):
    return use_case.list_recent(limit, offset)


@router.get("/session/{session_id}")
async def get_session_events(
    session_id: str,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    use_case: IngestEventUseCase = Depends(get_ingest_event_use_case)
):
    return use_case.list_by_session(session_id, limit, offset)