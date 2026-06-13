"""
GHARMIND AI — FastAPI Application Entry Point
India's First AI-powered Household Operating System.
"""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import v1_router
from app.config import settings
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    GharmindError,
    NotFoundError,
    ValidationError,
)
from app.core.middleware import RequestLoggingMiddleware, setup_cors
from app.db.session import check_database_health, init_db_extensions
from app.logging_config import configure_logging, get_logger

logger = get_logger(__name__)


# ── Application Lifespan ───────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Startup and shutdown lifecycle handler.
    On startup: configure logging, init DB extensions, verify connectivity.
    """
    # Startup
    configure_logging()
    logger.info(
        "gharmind_startup",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
    )

    # Initialize PostgreSQL extensions (vector, uuid-ossp, pg_trgm)
    try:
        await init_db_extensions()
        logger.info("db_extensions_ready")
    except Exception as e:
        logger.warning("db_extensions_init_failed", error=str(e))
        # Non-fatal — extensions may already exist

    # Verify DB connectivity
    db_healthy = await check_database_health()
    if not db_healthy:
        logger.warning("database_unreachable_on_startup")
    else:
        logger.info("database_connected")

    logger.info("gharmind_ready", host=settings.API_HOST, port=settings.API_PORT)

    yield  # Application runs here

    # Shutdown
    logger.info("gharmind_shutdown")


# ── Application Factory ────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="GHARMIND AI",
        description=(
            "India's First AI-powered Household Operating System.\n\n"
            "Understands household context, anticipates needs, and provides "
            "proactive intelligence — powered by AWS Bedrock Claude + Titan."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────
    setup_cors(app)
    app.add_middleware(RequestLoggingMiddleware)

    # ── Exception Handlers ────────────────────────────────────────────
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "type": "https://api.gharmind.in/errors/not-found",
                "title": "Resource not found",
                "status": 404,
                "detail": exc.message,
                "instance": str(request.url),
            },
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "type": "https://api.gharmind.in/errors/conflict",
                "title": "Conflict",
                "status": 409,
                "detail": exc.message,
            },
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "type": "https://api.gharmind.in/errors/forbidden",
                "title": "Forbidden",
                "status": 403,
                "detail": exc.message,
            },
        )

    @app.exception_handler(GharmindError)
    async def gharmind_error_handler(
        request: Request, exc: GharmindError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "type": f"https://api.gharmind.in/errors/{exc.error_code.lower()}",
                "title": exc.error_code.replace("_", " ").title(),
                "status": 500,
                "detail": exc.message,
            },
        )

    # ── Routers ───────────────────────────────────────────────────────
    app.include_router(v1_router)

    # ── System endpoints ──────────────────────────────────────────────
    @app.get("/system/health", tags=["System"])
    async def health_check() -> dict[str, Any]:
        """Health check endpoint — used by ECS, load balancers, and local dev."""
        db_ok = await check_database_health()
        return {
            "status": "healthy" if db_ok else "degraded",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "env": settings.APP_ENV,
            "database": "connected" if db_ok else "unreachable",
            "bedrock_mock": settings.BEDROCK_MOCK_RESPONSES,
            "skip_auth": settings.SKIP_AUTH,
            "timestamp": time.time(),
        }

    @app.get("/system/version", tags=["System"])
    async def version() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": "India's First AI-powered Household Operating System",
        }

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {
            "message": "GHARMIND AI — Household Operating System",
            "docs": "/docs",
            "health": "/system/health",
        }

    return app


# ── App instance ───────────────────────────────────────────────────────
app = create_app()


# ── CLI entry point ────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.is_development,
        log_level="debug" if settings.DEBUG else "info",
    )
