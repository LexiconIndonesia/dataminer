"""API v1 routers."""

from fastapi import APIRouter

from dataminer.api.v1 import sources

router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(sources.router, prefix="/dataminer", tags=["sources"])
