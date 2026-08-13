"""Capability Manager tracks agent abilities, sub-engines, health, and availability.
"""

from typing import List
from app.agents.software_engineer.autonomous.models import AgentCapability

class CapabilityManager:
    """Manages tracking status of available sub-engines."""

    def __init__(self) -> None:
        self.capabilities = [
            AgentCapability(engine_name="Project Manager Engine", supported_operations=["plan", "backlog", "sprints"]),
            AgentCapability(engine_name="Repository Analyzer", supported_operations=["analyze", "git"]),
            AgentCapability(engine_name="Code Intelligence Engine", supported_operations=["read", "symbols", "find_unused"]),
            AgentCapability(engine_name="Code Generation Engine", supported_operations=["generate", "write_code"]),
            AgentCapability(engine_name="Refactoring Engine", supported_operations=["refactor", "lint_fix"]),
            AgentCapability(engine_name="Testing Engine", supported_operations=["run_tests", "generate_tests"]),
            AgentCapability(engine_name="Debugging Engine", supported_operations=["debug", "analyze_traceback"]),
            AgentCapability(engine_name="Documentation Engine", supported_operations=["readme", "api_documentation"]),
            AgentCapability(engine_name="Deployment Engine", supported_operations=["docker", "kubernetes", "ci_pipeline"])
        ]

    def list_capabilities(self) -> List[AgentCapability]:
        """Lists active sub-engines registry status."""
        return self.capabilities

    def verify_capability(self, engine_name: str) -> bool:
        """Determines if target engine is loaded and available."""
        for cap in self.capabilities:
            if cap.engine_name == engine_name:
                return cap.is_available
        return False
