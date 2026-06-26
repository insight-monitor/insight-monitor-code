import asyncio
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.routes.health import router as health_router
from backend.routes.events import router as events_router
from backend.routes.sessions import router as sessions_router
from backend.infrastructure.di import (
    get_build_sessions_use_case,
    get_infer_intent_use_case,
)

logger = logging.getLogger(__name__)

POLL_INTERVAL = int(__import__("os").getenv("SESSION_BUILDER_POLL_SECONDS", "30"))
INFERENCE_POLL_INTERVAL = 60


@asynccontextmanager
async def lifespan(app: FastAPI):
    build_sessions = get_build_sessions_use_case()

    infer_intent = None
    if settings.api_key:
        infer_intent = get_infer_intent_use_case()
        logger.info("Inference pipeline initialized (model=%s)", settings.llm_model)
    else:
        logger.warning("API_KEY not set — inference pipeline disabled")

    sb_task = asyncio.create_task(_run_session_builder(build_sessions))
    ip_task = asyncio.create_task(_run_inference_pipeline(infer_intent))

    yield

    sb_task.cancel()
    ip_task.cancel()


async def _run_session_builder(use_case):
    while True:
        try:
            use_case.execute()
        except Exception as e:
            logger.error("BuildSessions error: %s", e)
        await asyncio.sleep(POLL_INTERVAL)


async def _run_inference_pipeline(use_case):
    while True:
        try:
            if use_case:
                use_case.execute_for_all_closed()
        except Exception as e:
            logger.error("InferIntent error: %s", e)
        await asyncio.sleep(INFERENCE_POLL_INTERVAL)


app = FastAPI(
    title="Insight Monitor API",
    version=settings.api_version,
    description="Backend API for Insight Monitor - contextual activity intelligence",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "detail": "Validation failed",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(_request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": "Internal server error"},
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
