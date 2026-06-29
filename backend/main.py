import asyncio
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes.health import router as health_router
from backend.routes.events import router as events_router
from backend.routes.sessions import router as sessions_router
from backend.routes.tickets import router as tickets_router
from backend.infrastructure.di import (
    get_build_sessions_use_case,
    get_infer_intent_use_case,
)

logger = logging.getLogger(__name__)

SESSION_BUILDER_POLL_SECONDS = 30
INFERENCE_POLL_SECONDS = 60


@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.infrastructure.di import get_db

    db = get_db()
    logger.info("Backend started (provider=%s, model=%s)", settings.llm_provider, settings.llm_model)

    sb_task = asyncio.create_task(_run_session_builder())
    ip_task = asyncio.create_task(_run_inference_pipeline())

    yield

    sb_task.cancel()
    ip_task.cancel()


async def _run_session_builder():
    while True:
        try:
            use_case = get_build_sessions_use_case()
            touched = use_case.execute()
            if touched:
                logger.debug("Session builder processed %d events", touched)
        except Exception as e:
            logger.error("Session builder error: %s", e)
        await asyncio.sleep(SESSION_BUILDER_POLL_SECONDS)


async def _run_inference_pipeline():
    while True:
        try:
            if settings.api_key:
                use_case = get_infer_intent_use_case()
                processed = use_case.execute_for_all_closed()
                if processed:
                    logger.debug("Inference processed %d closed sessions", processed)
        except Exception as e:
            logger.error("Inference pipeline error: %s", e)
        await asyncio.sleep(INFERENCE_POLL_SECONDS)


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
app.include_router(tickets_router)
