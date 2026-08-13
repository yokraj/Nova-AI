"""Workflow execution script for the Documentation Agent.
"""

from typing import Dict, Any
from app.agents.shared.workflow import BaseSpecialistWorkflow
from app.ai.agents.base.agent_result import AgentResult
from app.ai.agents.base.agent_session import AgentSession

class DocumentationWorkflow(BaseSpecialistWorkflow):
    """Orchestrates manual pages, OpenAPI schemas and READMEs compiles."""

    async def execute_documentation(self, session: AgentSession, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Returns created documents parameters reports."""
        session.record_state_change("BUSY", "BUSY", "Generating openapi swagger specifications and project readme manuals")
        return {
            "format": "Markdown / OpenAPI YAML",
            "files_written": ["openapi_spec.yaml", "README.md", "architecture_guide.md"],
            "sections": ["API Reference", "Deployment Setup", "Environment Variables"]
        }
