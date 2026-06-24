import asyncio
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes.health import router as health_router
from backend.routes.events import router as events_router
from backend.routes.sessions import router as sessions_router
from backend.pipeline.inference_pipeline import InferencePipeline
from backend.pipeline.session_builder import SessionBuilder, POLL_INTERVAL
from backend.storage.database import Database

logger = logging.getLogger(__name__)

INFERENCE_POLL_INTERVAL = 60

session_builder: SessionBuilder | None = None
inference_pipeline: InferencePipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global session_builder, inference_pipeline
    db = Database.get_instance(settings.db_path)
    session_builder = SessionBuilder(db)
    session_builder.start()

    # Inference pipeline is always initialized; it returns mock/fake intent data
    # when GEMINI_API_KEY is not set. TODO [Day 5]: Remove fake-data fallback once
    # a real LLM integration is in place and remove the GEMINI_API_KEY check.
    inference_pipeline = InferencePipeline(db)
    if settings.gemini_api_key:
        logger.info("Inference pipeline initialized (model=%s)", settings.gemini_model)
    else:
        logger.warning("GEMINI_API_KEY not set — using mock/fake intent responses")

    sb_task = asyncio.create_task(_run_session_builder())
    ip_task = asyncio.create_task(_run_inference_pipeline())

    yield

    sb_task.cancel()
    ip_task.cancel()
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


async def _run_inference_pipeline():
    while True:
        try:
            if inference_pipeline:
                inference_pipeline.process_closed_sessions()
        except Exception as e:
            logger.error("Inference pipeline error: %s", e)
        await asyncio.sleep(INFERENCE_POLL_INTERVAL)


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
