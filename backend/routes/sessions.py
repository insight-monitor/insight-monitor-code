from fastapi import APIRouter, HTTPException, Query

from backend.storage.database import Database
from backend.storage.repositories import (
    EventRepository,
    SessionRepository,
    IntentRepository,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])
session_repo = SessionRepository(Database.get_instance())
event_repo = EventRepository(Database.get_instance())
intent_repo = IntentRepository(Database.get_instance())


@router.get("")
async def list_sessions(
    status: str | None = Query(None),
    limit: int = Query(50, le=100),
):
    sessions = session_repo.find_all(status=status, limit=limit)
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/{session_id}")
async def get_session(session_id: str):
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
async def get_session_intent(session_id: str):
    intent = intent_repo.find_by_session(session_id)
    if not intent:
        raise HTTPException(
            status_code=404, detail="No intent record found for this session"
        )
    return intent


@router.post("/{session_id}/close")
async def close_session(session_id: str):
    session = session_repo.find_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.get("status") == "closed":
        return {"status": "already_closed", "session_id": session_id}
    session_repo.update(session_id, {"status": "closed"})
    return {"status": "closed", "session_id": session_id}
