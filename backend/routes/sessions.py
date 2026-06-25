from fastapi import APIRouter, Depends, HTTPException, Query

from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import (
    EventRepository,
    IntentRepository,
    SessionRepository,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_repo() -> SessionRepository:
    return SessionRepository(Database())


def get_event_repo() -> EventRepository:
    return EventRepository(Database())


def get_intent_repo() -> IntentRepository:
    return IntentRepository(Database())


@router.get("")
async def list_sessions(
    status: str | None = Query(None),
    limit: int = Query(50, le=100),
    session_repo: SessionRepository = Depends(get_session_repo),
):
    sessions = session_repo.find_all(status=status, limit=limit)
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repo),
    event_repo: EventRepository = Depends(get_event_repo),
    intent_repo: IntentRepository = Depends(get_intent_repo),
):
    session = session_repo.find_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    events = event_repo.find_by_session(session_id)
    intent = intent_repo.find_by_session(session_id)
    result = dict(session)
    result["events"] = events
    if intent:
        result["intent"] = intent
    return result


@router.get("/{session_id}/intent")
async def get_session_intent(
    session_id: str,
    intent_repo: IntentRepository = Depends(get_intent_repo),
):
    intent = intent_repo.find_by_session(session_id)
    if not intent:
        raise HTTPException(
            status_code=404, detail="No intent record found for this session"
        )
    return intent


@router.post("/{session_id}/close")
async def close_session(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repo),
):
    session = session_repo.find_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.get("status") == "closed":
        return {"status": "already_closed", "session_id": session_id}
    session_repo.update(session_id, {"status": "closed"})
    return {"status": "closed", "session_id": session_id}