from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "agent": "disconnected",
        "version": "0.1.0",
    }
