from fastapi import APIRouter

from backend.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "agent": "disconnected",
        "version": settings.api_version,
    }
