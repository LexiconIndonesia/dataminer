"""API v1 routers."""

from fastapi import APIRouter

from dataminer.api.v1 import fields, sources

router = APIRouter(prefix="/v1")

# Include sub-routers
router.include_router(sources.router, prefix="/dataminer", tags=["sources"])
router.include_router(fields.router, prefix="/dataminer", tags=["fields"])
