import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from app.config import settings
from api.routes.system import router as system_router
from api.routes import router as api_router
from app.logging_config import get_logger
from app.dev_auth import ensure_dev_token
from app.exceptions import handle_slate_runner_exception, SlateRunnerException
from app.middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware
from clients.db import db


@asynccontextmanager
async def lifespan(api: FastAPI):
    logger = get_logger()

    api.state.started_at = datetime.now(timezone.utc)
    api.state.settings = settings
    logger.info("%s booting up...", settings.SERVICE)

    db.connect()
    db.init_schema()
    db.seed()
    logger.info("database ready...")

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

    # Favicon route
    @api.get("/favicon.ico", include_in_schema=False)
    def favicon():
        file_path = os.path.join(os.path.dirname(__file__), "public", "static", "favicon.ico")
        return FileResponse(file_path)

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

    # Serve the built Vite backoffice console at root (FastAPI 0.138+ app.frontend()).
    # Path operations (/api, /docs, /favicon.ico, /static) are matched first, so the
    # SPA only handles paths the API does not. fallback="index.html" gives SPA routing.
    # check_dir=False lets the app boot before the frontend has been built.
    # api/src/main.py -> repo root holds the sibling frontend/ directory
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    frontend_dist = os.path.join(repo_root, "frontend", "dist")
    api.frontend("/", directory=frontend_dist, fallback="index.html", check_dir=False)

    return api


app = create_app()
