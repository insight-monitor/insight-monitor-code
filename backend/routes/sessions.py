from fastapi import APIRouter, Depends, HTTPException, Query

from backend.application.use_cases.get_session import GetSessionUseCase
from backend.infrastructure.di import get_get_session_use_case

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("")
async def list_sessions(
    status: str | None = Query(None),
    limit: int = Query(50, le=100),
    use_case: GetSessionUseCase = Depends(get_get_session_use_case),
):
    sessions = use_case.list_all(status=status, limit=limit)
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    use_case: GetSessionUseCase = Depends(get_get_session_use_case),
):
    result = use_case.execute(session_id, limit=limit, offset=offset)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.get("/{session_id}/intent")
async def get_session_intent(
    session_id: str,
    use_case: GetSessionUseCase = Depends(get_get_session_use_case),
):
    result = use_case.execute(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    if "intent" not in result:
        raise HTTPException(
            status_code=404, detail="No intent record found for this session"
        )
    return result["intent"]


@router.post("/{session_id}/close")
async def close_session(
    session_id: str,
    use_case: GetSessionUseCase = Depends(get_get_session_use_case),
):
    closed = use_case.close(session_id)
    if not closed:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "closed", "session_id": session_id}
