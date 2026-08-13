"""Validates AST structure and compilation of refactored content.
"""

import ast
from app.agents.software_engineer.refactoring.interfaces import Validator
from app.agents.software_engineer.refactoring.models import ValidationReport


class CodeValidator(Validator):
    """Checks syntax compile state using python AST parser."""

    def validate_code(self, file_path: str, code: str) -> ValidationReport:
        """Parses python source checks.

        Args:
            file_path: Relative target file path.
            code: Source code content string.

        Returns:
            ValidationReport payload.
        """
        try:
            ast.parse(code, filename=file_path)
            return ValidationReport(is_valid=True)
        except SyntaxError as e:
            msg = f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"
            return ValidationReport(is_valid=False, errors=[msg])
        except Exception as e:
            return ValidationReport(is_valid=False, errors=[str(e)])
