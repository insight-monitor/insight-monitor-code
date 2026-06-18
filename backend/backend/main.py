from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes.health import router as health_router
from backend.routes.events import router as events_router
from backend.routes.sessions import router as sessions_router

app = FastAPI(
    title="Insight Monitor API",
    version=settings.api_version,
    description="Backend API for Insight Monitor - contextual activity intelligence",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(events_router)
app.include_router(sessions_router)
