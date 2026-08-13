"""Formatter maintaining code spacing layout standards.
"""

from app.agents.software_engineer.generator.models import FormatterResult, StyleProfile


class TestingCodeFormatter:
    """Standardizes spacing in generated test files."""

    def format_code(self, code: str, style: StyleProfile) -> FormatterResult:
        """Applies indentation replacement formats.

        Args:
            code: Test source code string.
            style: Indent rules configuration.

        Returns:
            FormatterResult.
        """
        try:
            lines = code.splitlines()
            formatted = []
            for line in lines:
                if line.startswith(" ") or line.startswith("\t"):
                    indent_chars = len(line) - len(line.lstrip())
                    depth = indent_chars // 4 if not line.startswith("\t") else indent_chars
                    new_indent = style.indentation * depth
                    formatted.append(f"{new_indent}{line.lstrip()}")
                else:
                    formatted.append(line)
            return FormatterResult(success=True, content="\n".join(formatted))
        except Exception as e:
            return FormatterResult(success=False, content=code, error=str(e))
