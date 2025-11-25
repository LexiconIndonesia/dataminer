"""Health check endpoints."""

import asyncio
from datetime import UTC, datetime

from fastapi import APIRouter, status

from dataminer import __version__
from dataminer.api.generated import HealthResponse, ReadinessResponse
from dataminer.core.config import get_settings

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns the health status of the service",
)
async def health_check() -> HealthResponse:
    """Check if the service is healthy."""
    return HealthResponse(version=__version__, timestamp=datetime.now(UTC))


async def _check_database() -> bool:
    """Check database connectivity."""
    try:
        import asyncpg

        settings = get_settings()
        db_url = str(settings.database_url).replace("postgresql://", "")
        conn = await asyncio.wait_for(asyncpg.connect(db_url), timeout=2.0)
        await conn.close()
        return True
    except Exception:
        return False


async def _check_redis() -> bool:
    """Check Redis connectivity."""
    try:
        from redis.asyncio import from_url

        settings = get_settings()
        redis = from_url(str(settings.redis_url))
        await asyncio.wait_for(redis.ping(), timeout=2.0)
        await redis.close()  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


async def _check_nats() -> bool:
    """Check NATS connectivity."""
    try:
        from nats.aio.client import Client as NATS

        settings = get_settings()
        nc = NATS()
        await asyncio.wait_for(nc.connect(settings.nats_url), timeout=2.0)
        await nc.close()
        return True
    except Exception:
        return False


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Returns the readiness status of the service and its dependencies",
)
async def readiness_check() -> ReadinessResponse:
    """Check if the service is ready to accept requests."""
    # Run all health checks concurrently
    db_check, redis_check, nats_check = await asyncio.gather(
        _check_database(), _check_redis(), _check_nats(), return_exceptions=True
    )

    checks = {
        "database": db_check if isinstance(db_check, bool) else False,
        "redis": redis_check if isinstance(redis_check, bool) else False,
        "nats": nats_check if isinstance(nats_check, bool) else False,
    }

    return ReadinessResponse(
        ready=all(checks.values()),
        checks=checks,
    )
