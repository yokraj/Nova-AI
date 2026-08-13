"""Experience Distiller converting repeated workflows into reusable skills and templates.
"""

from typing import List
from app.ai.self_improvement.interfaces import IExperienceDistiller
from app.ai.self_improvement.models import ExperiencePackage


class ExperienceDistiller(IExperienceDistiller):
    """Distills repeated workflows into reusable Skills, Automation Templates, and Mission Templates."""

    def distill_experience(self, workflow_name: str, steps: List[str]) -> ExperiencePackage:
        """Converts workflow steps into ExperiencePackage.

        Args:
            workflow_name: Workflow name string.
            steps: List of workflow step descriptions.

        Returns:
            ExperiencePackage payload instance.
        """
        clean_name = workflow_name.lower().replace(" ", "_")
        return ExperiencePackage(
            name=workflow_name,
            workflow_steps=steps,
            reusable_skill_id=f"skill_{clean_name}",
            automation_template_id=f"tmpl_auto_{clean_name}",
            mission_template_id=f"tmpl_msn_{clean_name}",
        )
