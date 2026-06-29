import time

from fastapi import APIRouter

from backend.config import settings

router = APIRouter(tags=["health"])

_agent_last_seen: float | None = None
AGENT_HEARTBEAT_TIMEOUT = 60


def record_agent_heartbeat():
    global _agent_last_seen
    _agent_last_seen = time.time()


def get_agent_status() -> dict:
    if _agent_last_seen is None:
        return {"status": "offline", "version": settings.api_version, "last_seen": None}

    now = time.time()
    online = (now - _agent_last_seen) <= AGENT_HEARTBEAT_TIMEOUT
    return {
        "status": "online" if online else "offline",
        "version": settings.api_version,
        "last_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(_agent_last_seen)),
    }


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "agent": get_agent_status(),
        "api_version": settings.api_version,
    }


@router.post("/heartbeat")
async def agent_heartbeat():
    record_agent_heartbeat()
    return {"status": "ok"}
