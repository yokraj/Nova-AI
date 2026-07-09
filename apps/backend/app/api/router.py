"""Central root API router registry for Nova AI.

Mounts the health monitoring systems and version 1 endpoints
into a unified root API router.
"""

from fastapi import APIRouter

from app.api.routers.health import router as health_router
from app.api.v1.api import router as v1_router

router = APIRouter(prefix="/api")

# Register system health metrics router
router.include_router(health_router)

# Register versioned API router under the v1 namespace prefix
router.include_router(v1_router, prefix="/v1")
