"""Context System compiling shared variables and profiles snapshots.
"""

from typing import Optional, Dict, Any
from app.ai.agents.models import AgentContext

class ContextSystem:
    """Builder generating instances of the Pydantic AgentContext model."""

    def create_context(
        self,
        conversation_id: Optional[str] = None,
        project_root: Optional[str] = None,
        user_id: Optional[str] = None,
        permissions_profile: str = "ReadOnly",
        runtime_env: Optional[Dict[str, Any]] = None
    ) -> AgentContext:
        """Returns initialized AgentContext configuration structures."""
        return AgentContext(
            conversation_id=conversation_id,
            project_root=project_root,
            user_id=user_id,
            permissions_profile=permissions_profile,
            runtime_env=runtime_env or {}
        )
