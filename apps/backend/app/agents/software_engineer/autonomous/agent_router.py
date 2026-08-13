"""Agent Router selects correct sub-engine based on task details.
"""

from app.agents.software_engineer.autonomous.interfaces import IAgentRouter

class LocalAgentRouter(IAgentRouter):
    """Maps task descriptions to engine identifiers."""

    def route_request(self, task_description: str) -> str:
        """Determines the correct capability engine to execute this task."""
        desc = task_description.lower()

        if "unused" in desc or "intelligence" in desc or "structure" in desc or "find" in desc:
            return "Code Intelligence Engine"
        elif "fix" in desc or "debug" in desc or "error" in desc or "resolve" in desc:
            return "Debugging Engine"
        elif "deploy" in desc or "docker" in desc or "kubernetes" in desc or "helm" in desc or "ci/cd" in desc:
            return "Deployment Engine"
        elif "test" in desc or "pytest" in desc or "coverage" in desc:
            return "Testing Engine"
        elif "project" in desc or "milestone" in desc or "sprint" in desc or "backlog" in desc:
            return "Project Manager Engine"
        elif "analyze repo" in desc or "branches" in desc or "git" in desc:
            return "Repository Analyzer"
        elif "refactor" in desc or "clean code" in desc:
            return "Refactoring Engine"
        elif "document" in desc or "readme" in desc or "api docs" in desc:
            return "Documentation Engine"
        else:
            return "Code Generation Engine"
