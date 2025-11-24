"""FastAPI application factory."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dataminer import __version__
from dataminer.api import health
from dataminer.api.errors import setup_exception_handlers
from dataminer.api.middleware import setup_middleware
from dataminer.api.v1 import router as v1_router
from dataminer.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan events."""
    settings = get_settings()

    # Startup
    logger.info(
        "Starting application",
        extra={
            "app_name": settings.app_name,
            "version": __version__,
            "environment": settings.environment,
        },
    )

    # TODO: Initialize database connections, Redis, NATS, etc.

    yield

    # Shutdown
    logger.info("Shutting down application")

    # TODO: Close database connections, Redis, NATS, etc.


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure FastAPI application."""
    if settings is None:
        settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name.title(),
        description="Document extraction service for legal documents",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup middleware
    setup_middleware(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Root endpoint
    @app.get(
        "/",
        tags=["Root"],
        response_class=JSONResponse,
        summary="Root Endpoint",
    )
    async def root() -> dict[str, str]:
        """Root endpoint with basic info."""
        return {
            "service": settings.app_name,
            "version": __version__,
            "status": "running",
        }

    # Include routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(v1_router)

    logger.info("Application created successfully")

    return app


# Create app instance for uvicorn
app = create_app()
