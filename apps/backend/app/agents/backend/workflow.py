"""Workflow execution script for the Backend Agent.
"""

from typing import Dict, Any
from app.agents.shared.workflow import BaseSpecialistWorkflow
from app.ai.agents.base.agent_result import AgentResult
from app.ai.agents.base.agent_session import AgentSession

class BackendWorkflow(BaseSpecialistWorkflow):
    """Orchestrates API routers and models files constructions."""

    async def execute_backend(self, session: AgentSession, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Returns generated backend code structures templates."""
        session.record_state_change("BUSY", "BUSY", "Drafting REST endpoint routes and user authentication code blocks")
        return {
            "controllers_written": ["auth_router.py", "user_routes.py", "api_v1.py"],
            "endpoints": [
                "POST /api/v1/auth/login",
                "POST /api/v1/auth/signup",
                "GET /api/v1/users/profile"
            ],
            "dependencies_added": ["python-jose", "passlib", "bcrypt"]
        }
