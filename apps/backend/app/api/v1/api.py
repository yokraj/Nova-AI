"""Version 1 API router packaging for Nova AI.

Aggregates all REST endpoint sub-routers defined under the v1 API lifecycle.
"""

from fastapi import APIRouter

from app.identity.api.auth_router import router as auth_router
from app.identity.api.user_router import router as user_router

router = APIRouter()

# Mount auth endpoints
router.include_router(auth_router)

# Mount user query endpoints
router.include_router(user_router)

# Mount conversation endpoints
from app.conversation.api.conversation_router import router as conversation_router
router.include_router(conversation_router)

# Mount workflow engine endpoints
from app.automation import workflows_router

router.include_router(workflows_router)

