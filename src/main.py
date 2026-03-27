import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.templating import Jinja2Templates
from app.config import settings
from api.routes.system import router as system_router
from api.routes import router as api_router
from db.db import engine
from app.logging_config import get_logger
from app.exceptions import handle_slate_runner_exception, SlateRunnerException
from app.middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(api: FastAPI):
    logger = get_logger()

    api.state.started_at = datetime.now(timezone.utc)
    api.state.settings = settings
    logger.info("%s booting up...", settings.SERVICE)

    # Get DB connection up and ready.
    try:
        with engine.connect() as conn:
            logger.info("database ready...")
    except Exception as e:
        logger.error("database connection failed on startup: %s", e)

    try:
        yield
    finally:
        engine.dispose()
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

    templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "public"))

    # Root endpoint
    @api.get("/", response_class=HTMLResponse, tags=["root"])
    def root(request: Request):
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": getattr(request.app, "title"),
                "description": getattr(request.app, "description"),
                "version": getattr(request.app, "version"),
                "environment": settings.ENVIRONMENT
            }
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
    return api


app = create_app()
