from fastapi import APIRouter, Query

from backend.storage.database import Database
from backend.storage.repositories import SessionRepository, IntentRepository

router = APIRouter(prefix="/sessions", tags=["sessions"])
session_repo = SessionRepository(Database.get_instance())
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
        return {"error": "Session not found"}, 404

    intent = intent_repo.find_by_session(session_id)
    result = dict(session)
    if intent:
        result["intent"] = intent
    return result


@router.get("/{session_id}/intent")
async def get_session_intent(session_id: str):
    intent = intent_repo.find_by_session(session_id)
    if not intent:
        return {"error": "No intent record found for this session"}, 404
    return intent
