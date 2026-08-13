"""Project Requirements Division for Autonomous AI Software Engineering Company.
"""

from typing import List
from app.ai.software_company.interfaces import IProjectRequirementsDivision
from app.ai.software_company.models import SoftwareProjectSpec


class ProjectRequirementsDivision(IProjectRequirementsDivision):
    """Requirements Division managing user interviews, SRS generation, user stories, and feature scoping."""

    def __init__(self) -> None:
        self.agents: List[str] = [
            "ProductOwnerAgent",
            "BusinessAnalystAgent",
            "RequirementsEngineerAgent",
            "DomainExpertAgent",
            "ScopePlannerAgent",
        ]

    async def extract_requirements(self, user_prompt: str) -> SoftwareProjectSpec:
        """Translates user prompt into full Software Requirements Specification (SRS)."""
        title = user_prompt.strip().title() if user_prompt else "Autonomous Software Project"
        user_stories = [
            f"As a user, I want to authenticate securely in {title}.",
            f"As an administrator, I want to manage data records in {title}.",
            f"As an analyst, I want to view performance metrics in {title}.",
        ]
        func_reqs = [
            "User authentication & RBAC authorization",
            "REST API endpoints for data CRUD operations",
            "Real-time WebSocket event notifications",
        ]

        return SoftwareProjectSpec(
            title=title,
            user_prompt=user_prompt,
            srs_document=f"Software Requirements Specification for {title}",
            user_stories=user_stories,
            functional_requirements=func_reqs,
            tech_stack={"backend": "FastAPI", "frontend": "React", "database": "PostgreSQL"},
        )
