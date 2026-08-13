"""Repair Engine suggesting fixes for failed test assertions.
"""

from app.agents.software_engineer.testing.interfaces import RepairEngine
from app.agents.software_engineer.testing.models import (
    FailureReport,
    RepairSuggestion,
    TestingContext,
)


class LocalTestRepairEngine(RepairEngine):
    """Generates recommend patches utilizing model prompts."""

    def suggest_repairs(
        self, failure: FailureReport, context: TestingContext
    ) -> RepairSuggestion:
        """Formulates patch modifications.

        Args:
            failure: Detailed failure report.
            context: Context.

        Returns:
            RepairSuggestion.
        """
        # Suggestion generator fallback suggestion
        rec_patch = (
            "# Recommendation: check mock assertions\n"
            "# Replace: assert result is not None\n"
            "# With: assert result == expected_value"
        )

        return RepairSuggestion(
            target_test_file=context.target_module or "test_file.py",
            failing_test_name="test_placeholder",
            recommended_patch=rec_patch,
            explanation=f"Assertion failed on lines: {failure.message}",
        )
