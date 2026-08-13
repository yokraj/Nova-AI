"""Technology Selection Engine selecting stacks, frameworks, databases, and tooling.
"""

from typing import Any, Dict, List
from app.ai.copilot.interfaces import ITechnologySelector
from app.ai.copilot.models import ArchitectureDesign, RequirementDocument, TechStack


class TechnologySelector(ITechnologySelector):
    """Technology Selection Engine picking technologies matching requirement criteria."""

    async def select_technologies(self, reqs: RequirementDocument, arch: ArchitectureDesign) -> TechStack:
        """Selects technologies, frameworks, and databases for a project.

        Args:
            reqs: RequirementDocument.
            arch: ArchitectureDesign.

        Returns:
            TechStack model instance.
        """
        prefs = [p.lower() for p in reqs.technology_preferences]

        languages = ["python", "typescript"]
        frameworks = ["FastAPI", "React"]
        databases = ["PostgreSQL", "SQLite"]
        messaging = ["Redis PubSub"]
        containers = ["Docker", "Docker Compose"]
        cloud = ["Local-First Subsystem", "AWS S3 / Local MinIO"]
        testing = ["pytest", "jest"]
        tools = ["git", "uv", "pnpm", "eslint"]

        if any("node" in p or "nest" in p for p in prefs):
            languages = ["typescript", "javascript"]
            frameworks = ["NestJS", "React"]

        elif any("java" in p or "spring" in p for p in prefs):
            languages = ["java", "typescript"]
            frameworks = ["Spring Boot", "React"]

        elif any("go" in p for p in prefs):
            languages = ["go", "typescript"]
            frameworks = ["Gin", "Vue.js"]

        elif any("flutter" in p for p in prefs):
            languages = ["dart", "python"]
            frameworks = ["Flutter", "FastAPI"]

        if any("mongo" in p for p in prefs):
            databases = ["MongoDB", "Redis"]

        return TechStack(
            languages=languages,
            frameworks=frameworks,
            databases=databases,
            messaging=messaging,
            containerization=containers,
            cloud_providers=cloud,
            testing_frameworks=testing,
            dev_tools=tools,
        )
