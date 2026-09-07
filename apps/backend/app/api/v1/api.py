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

# Mount enterprise memory endpoints
from app.memory.api import router as memory_router

router.include_router(memory_router)

# Mount enterprise vector engine endpoints
from app.vector_memory.api import router as vector_router

router.include_router(vector_router)

# Mount enterprise hybrid RAG endpoints
from app.rag.api import router as rag_router

router.include_router(rag_router)

# Mount enterprise knowledge graph endpoints
from app.knowledge_graph.api import router as graph_router

router.include_router(graph_router)

# Mount enterprise code intelligence endpoints
from app.code_intelligence.api import router as code_router

router.include_router(code_router)

# Mount enterprise context engine endpoints
from app.context_engine.api import router as context_router

router.include_router(context_router)

# Mount enterprise platform validation endpoints
from app.platform_validation.api import router as validation_router

router.include_router(validation_router)

# Mount enterprise inference gateway endpoints
from app.inference.api import router as inference_router

router.include_router(inference_router)

# Mount learned skills endpoints
from app.api.v1.skills_router import router as skills_router
router.include_router(skills_router)

# Mount mission control endpoints
from app.api.v1.missions_router import router as missions_router
router.include_router(missions_router)

# Mount agent workforce endpoints
from app.api.v1.agents_router import router as agents_router
router.include_router(agents_router)

# Mount audit event endpoints
from app.api.v1.audit_router import router as audit_router
router.include_router(audit_router)

# Mount health monitoring endpoints
from app.api.routers.health import router as health_router
router.include_router(health_router)




