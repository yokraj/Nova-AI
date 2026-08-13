"""Deployment Planner orchestrates the stages of the preparation.
"""

from typing import Dict, Any
from app.agents.software_engineer.deployment.models import DeploymentRequest, DeploymentPlan

class DeploymentPlanner:
    """Plans sequence steps for deployment preparation pipeline."""

    def plan_deployment(self, request: DeploymentRequest, context: Dict[str, Any]) -> DeploymentPlan:
        """Determines target stages needed based on target platform configurations."""
        stages = [
            "Project Analysis",
            "Environment Detection",
            "Dependency Validation",
            "Build Planning",
            "Container Generation"
        ]

        if request.target_platform in ("kubernetes", "helm"):
            stages.append("Infrastructure Generation")

        stages.extend([
            "CI/CD Generation",
            "Deployment Validation",
            "Release Preparation",
            "Monitoring Setup",
            "Deployment Report"
        ])

        return DeploymentPlan(
            stages=stages,
            status="planned",
        )
