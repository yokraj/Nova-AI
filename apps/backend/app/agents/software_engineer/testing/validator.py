"""Validator validating generated test syntax.
"""

from app.agents.software_engineer.testing.models import ValidationReport
from app.agents.software_engineer.testing.utils import safe_compile_code


class GeneratedTestValidator:
    """Verifies that generated test scripts compile without errors."""

    def validate_code(self, file_path: str, code: str) -> ValidationReport:
        """Parses testing source checks.

        Args:
            file_path: Relative target file path.
            code: Testing source code.

        Returns:
            ValidationReport.
        """
        success, err = safe_compile_code(code, file_path)
        if not success:
            return ValidationReport(is_valid=False, errors=[err or "Unknown compilation error"])
        return ValidationReport(is_valid=True)
