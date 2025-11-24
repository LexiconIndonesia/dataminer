"""API error handling."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    message: str
    detail: Any = None
    request_id: str | None = None


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, "request_id", None)

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            request_id=request_id,
        ).model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    request_id = getattr(request.state, "request_id", None)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="Request validation failed",
            detail=exc.errors(),
            request_id=request_id,
        ).model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    request_id = getattr(request.state, "request_id", None)

    logger.exception(
        "Unhandled exception occurred",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
        },
    )

    # Don't leak internal error details in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An internal server error occurred",
            request_id=request_id,
        ).model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers for the application."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
