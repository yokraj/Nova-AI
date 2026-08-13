"""Formats refactored code matching target StyleProfile rules.
"""

from app.agents.software_engineer.generator.models import FormatterResult, StyleProfile
from app.agents.software_engineer.refactoring.interfaces import Formatter


class RefactoringCodeFormatter(Formatter):
    """Aligns line-indents layout with workspace conventions."""

    def format_code(self, code: str, style: StyleProfile) -> FormatterResult:
        """Indents source lines matching active parameters.

        Args:
            code: Source code string to format.
            style: Indent spacing guideline settings.

        Returns:
            FormatterResult structure.
        """
        # Re-use python space-indenter logic
        try:
            lines = code.splitlines()
            formatted = []
            for line in lines:
                if line.startswith(" ") or line.startswith("\t"):
                    # Calculate indent depth and re-apply style profile indentation
                    indent_chars = len(line) - len(line.lstrip())
                    depth = indent_chars // 4 if not line.startswith("\t") else indent_chars
                    new_indent = style.indentation * depth
                    formatted.append(f"{new_indent}{line.lstrip()}")
                else:
                    formatted.append(line)
            return FormatterResult(success=True, content="\n".join(formatted))
        except Exception as e:
            return FormatterResult(success=False, content=code, error=str(e))
