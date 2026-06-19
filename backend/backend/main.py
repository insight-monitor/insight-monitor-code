import asyncio
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes.health import router as health_router
from backend.routes.events import router as events_router
from backend.routes.sessions import router as sessions_router
from backend.pipeline.session_builder import SessionBuilder, POLL_INTERVAL
from backend.storage.database import Database

logger = logging.getLogger(__name__)

session_builder: SessionBuilder | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global session_builder
    db = Database.get_instance(settings.db_path)
    session_builder = SessionBuilder(db)
    session_builder.start()

    task = asyncio.create_task(_run_session_builder())

    yield

    task.cancel()
    if session_builder:
        session_builder.stop()


async def _run_session_builder():
    while True:
        try:
            if session_builder:
                session_builder.process_pending_events()
        except Exception as e:
            logger.error("Session builder error: %s", e)
        await asyncio.sleep(POLL_INTERVAL)


app = FastAPI(
    title="Insight Monitor API",
    version=settings.api_version,
    description="Backend API for Insight Monitor - contextual activity intelligence",
    lifespan=lifespan,
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
