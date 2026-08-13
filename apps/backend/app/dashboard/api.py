"""Dashboard API Aggregator Module.

Combines HTTP REST routes and WebSocket streaming routes into unified API routers
for module-level registration.
"""

from fastapi import APIRouter

from app.dashboard.routes import router as dashboard_rest_router
from app.dashboard.websocket import router as dashboard_ws_router

router = APIRouter()

router.include_router(dashboard_rest_router)
router.include_router(dashboard_ws_router)
