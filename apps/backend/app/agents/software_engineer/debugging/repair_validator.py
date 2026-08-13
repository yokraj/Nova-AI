"""Repair Validator compiling proposed code changes syntax correctness.
"""

from app.agents.software_engineer.debugging.interfaces import RepairValidator
from app.agents.software_engineer.debugging.models import RepairPlan, RepairValidation
from app.agents.software_engineer.debugging.utils import safe_parse_ast


class WorkspaceRepairValidator(RepairValidator):
    """Checks generated Python patches syntax correctness."""

    def validate_repair(self, plan: RepairPlan) -> RepairValidation:
        """Runs compile checks.

        Args:
            plan: The repair plan.

        Returns:
            RepairValidation.
        """
        errors = []

        for sug in plan.suggestions:
            # Validate compile-ability
            success, err = safe_parse_ast(sug.replacement_code, sug.file_path)
            if not success:
                errors.append(f"Compile check failed for {sug.file_path}: {err}")

        return RepairValidation(is_valid=len(errors) == 0, errors=errors)
