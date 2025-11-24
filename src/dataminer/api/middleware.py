"""API middleware for request/response handling."""

import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """Add request ID to request state and response headers."""
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """Log request and response details."""
        request_id = getattr(request.state, "request_id", "unknown")
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_host": request.client.host if request.client else None,
            },
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "Request failed with exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                },
            )
            raise

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            },
        )

        return response


def setup_middleware(app: ASGIApp) -> None:
    """Configure all middleware for the application."""
    # Note: Middleware is applied in reverse order
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
