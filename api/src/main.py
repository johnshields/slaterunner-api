import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router as api_router
from api.routes.system import router as system_router
from app.config import settings
from app.dev_auth import ensure_boot_token, ensure_dev_token
from app.exceptions import SlateRunnerException, handle_slate_runner_exception
from app.logging_config import get_logger
from app.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from db import db


@asynccontextmanager
async def lifespan(api: FastAPI):
    logger = get_logger()

    api.state.started_at = datetime.now(UTC)
    api.state.settings = settings
    logger.info("%s booting up...", settings.SERVICE)

    db.connect()
    db.init_schema()
    db.seed()
    logger.info("database ready...")

    ensure_boot_token(logger)
    ensure_dev_token(logger)

    try:
        yield
    finally:
        db.close()
        logger.info("%s shutting down...", settings.SERVICE)


# Init FastAPI
def create_app() -> FastAPI:
    api = FastAPI(
        title=settings.SERVICE,
        version=settings.VERSION,
        description=settings.DESC,
        lifespan=lifespan,
    )

    # Add middleware in order
    api.add_middleware(SecurityHeadersMiddleware)
    api.add_middleware(RequestLoggingMiddleware)
    api.add_middleware(RateLimitMiddleware)
    api.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount all static files
    api.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "public", "static")), name="static")

    # Exception handlers
    @api.exception_handler(SlateRunnerException)
    async def slate_runner_exception_handler(exc: SlateRunnerException):
        return JSONResponse(
            status_code=400,
            content=handle_slate_runner_exception(exc).detail
        )

    @api.exception_handler(RequestValidationError)
    async def validation_exception_handler(exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "message": "Validation error",
                "details": exc.errors()
            }
        )

    # Include API routes
    api.include_router(system_router, prefix="/api")
    api.include_router(api_router, prefix="/api/v1")

    # Serve the built Vite console at root when present, else serve the API alone
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    app_dist = os.path.join(repo_root, "app", "dist")
    if os.path.isdir(app_dist):
        api.frontend("/", directory=app_dist, fallback="index.html")
    else:
        get_logger().warning("app build not found at %s; serving API only", app_dist)

    return api


app = create_app()
