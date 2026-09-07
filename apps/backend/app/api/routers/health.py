"""Health checking endpoints for Nova AI API service.

Exposes status routing checking backend availability (/health, /live),
active database sockets readiness (/ready), and metrics placeholders (/metrics).
"""

from fastapi import APIRouter
from sqlalchemy.sql import text

from app.core.constants import HEALTH_STATUS_OK
from app.core.version import VERSION
from app.database.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
@router.get("/system/health")
async def health() -> dict:
    """Returns overall platform status and app version."""
    return {"status": HEALTH_STATUS_OK, "version": VERSION}



@router.get("/live")
async def live() -> dict:
    """Checks whether the application process is running."""
    return {"status": HEALTH_STATUS_OK}


@router.get("/ready")
async def ready() -> dict:
    """Verifies backend database connection pool readiness."""
    try:
        # Connect to the async pool and execute a simple test command
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return {"status": HEALTH_STATUS_OK, "database": "connected"}
    except Exception as error:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(error),
        }


@router.get("/metrics")
async def metrics() -> dict:
    """Returns instrumentation performance metrics. (Placeholder)."""
    return {
        "metrics_enabled": False,
        "message": "Metrics telemetry details will be integrated in Phase 2.",
    }
