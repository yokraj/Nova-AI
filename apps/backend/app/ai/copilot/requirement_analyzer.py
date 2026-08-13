"""Requirement Analysis Engine extracting structured specifications from prompts.
"""

from typing import Any, Dict, List
from app.ai.copilot.interfaces import IRequirementAnalyzer
from app.ai.copilot.models import RequirementDocument


class RequirementAnalyzer(IRequirementAnalyzer):
    """Requirement Analysis Engine parsing user prompts into structured RequirementDocument specifications."""

    async def analyze_requirements(self, prompt: str, project_name: str = "NovaProject") -> RequirementDocument:
        """Parses prompt into structured requirements document.

        Args:
            prompt: Natural language requirements text.
            project_name: Title of project.

        Returns:
            RequirementDocument instance.
        """
        p_lower = prompt.lower()

        business_goals = [
            f"Deliver high-quality software system for: {prompt[:60]}",
            "Provide automated user workflows and local data storage",
            "Ensure 99.9% uptime and zero-cost local execution",
        ]

        functional_requirements = [
            f"Core system functionality: {prompt}",
            "User authentication and session management",
            "REST API endpoints for data retrieval and persistence",
            "Interactive dashboard and reporting capabilities",
        ]

        non_functional_requirements = [
            "Sub-100ms response time for API endpoints",
            "Local-first storage with offline capability",
            "Windows-first environment integration",
        ]

        constraints = [
            "Zero paid external API dependencies",
            "Local-first CPU/GPU hardware resource limits",
        ]

        tech_prefs = ["Python", "FastAPI", "React", "PostgreSQL", "Docker"]
        if "node" in p_lower or "nest" in p_lower:
            tech_prefs = ["Node.js", "NestJS", "TypeScript", "React", "PostgreSQL"]
        elif "java" in p_lower or "spring" in p_lower:
            tech_prefs = ["Java", "Spring Boot", "React", "PostgreSQL"]
        elif "go" in p_lower or "gin" in p_lower:
            tech_prefs = ["Go", "Gin", "Vue.js", "PostgreSQL"]
        elif "flutter" in p_lower:
            tech_prefs = ["Dart", "Flutter", "Python", "FastAPI"]

        security_requirements = [
            "OAuth2 JWT bearer token authorization",
            "Bcrypt password hashing and input sanitization",
            "OWASP Top 10 security compliance",
        ]

        performance_targets = [
            "API p95 latency < 50ms",
            "Concurrency support for up to 500 active connections",
        ]

        acceptance_criteria = [
            "All unit and integration tests pass with 100% success rate",
            "Clean compilation with zero static analysis warnings",
            "Containerized deployment configuration verified",
        ]

        return RequirementDocument(
            project_name=project_name,
            business_goals=business_goals,
            functional_requirements=functional_requirements,
            non_functional_requirements=non_functional_requirements,
            constraints=constraints,
            technology_preferences=tech_prefs,
            security_requirements=security_requirements,
            performance_targets=performance_targets,
            acceptance_criteria=acceptance_criteria,
        )
