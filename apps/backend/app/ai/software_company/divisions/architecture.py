"""System Architecture Division for Autonomous AI Software Engineering Company.
"""

from typing import List
from app.ai.software_company.interfaces import ISystemArchitectureDivision
from app.ai.software_company.models import SoftwareArchitectureBlueprint, SoftwareProjectSpec


class SystemArchitectureDivision(ISystemArchitectureDivision):
    """Architecture Division creating system blueprints, component hierarchies, and folder structures."""

    def __init__(self) -> None:
        self.agents: List[str] = [
            "SolutionArchitectAgent",
            "SoftwareArchitectAgent",
            "DatabaseArchitectAgent",
            "InfrastructureArchitectAgent",
            "CloudArchitectAgent",
            "SecurityArchitectAgent",
        ]

    async def design_architecture(self, spec: SoftwareProjectSpec) -> SoftwareArchitectureBlueprint:
        """Designs system architecture blueprint and component hierarchy."""
        components = [
            "API Gateway & Auth Middleware",
            "FastAPI Core Service Engine",
            "PostgreSQL Database & Alembic Migrations",
            "React Web UI Frontend",
            "Docker Container Topology",
        ]
        folders = [
            "apps/backend/app/api/v1/",
            "apps/backend/app/core/",
            "apps/backend/app/database/",
            "apps/frontend/src/components/",
            "apps/frontend/src/pages/",
        ]

        return SoftwareArchitectureBlueprint(
            project_id=spec.project_id,
            components=components,
            folder_structure=folders,
            caching_strategy="Redis In-Memory Cache",
            deployment_topology="Docker Containerized Microservices",
        )
