"""Language provider registering syntax checkers and formatters for target languages.
"""

import ast
from typing import Dict

from app.agents.software_engineer.generator.interfaces import LanguageProvider
from app.agents.software_engineer.generator.models import (
    FormatterResult,
    StyleProfile,
    ValidationResult,
)


class PythonLanguageProvider(LanguageProvider):
    """Provides formatting and validation hooks specific to Python programming language."""

    def get_language(self) -> str:
        return "python"

    def validate(self, file_path: str, code: str) -> ValidationResult:
        """Parses generated Python code using AST to check for syntax errors.

        Args:
            file_path: Relative target file path.
            code: Source code string to validate.

        Returns:
            ValidationResult report.
        """
        try:
            ast.parse(code, filename=file_path)
            return ValidationResult(is_valid=True)
        except SyntaxError as e:
            error_msg = f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg} -> '{e.text}'"
            return ValidationResult(is_valid=False, errors=[error_msg])
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[f"AST Parse failed: {str(e)}"])

    def format(self, code: str, style: StyleProfile) -> FormatterResult:
        """Applies indentation and blank line formatting constraints to python code.

        Args:
            code: Source code string to format.
            style: Indentation and layout rules configuration.

        Returns:
            FormatterResult structure.
        """
        # A simple, robust space-indenter that reformats indentation spacing.
        # This replaces indentation spacing to match the style profile.
        # For a thorough formatter, we inspect line starting spaces.
        try:
            lines = code.splitlines()
            formatted_lines = []
            for line in lines:
                # If space-indented and target is different, convert it
                match = re.match(r"^(\s+)(.*)$", line)
                if match:
                    indent_str, content = match.groups()
                    # Calculate depth assuming 4 spaces or tabs
                    if "\t" in indent_str:
                        depth = len(indent_str)
                    else:
                        depth = len(indent_str) // 4

                    new_indent = style.indentation * depth
                    formatted_lines.append(f"{new_indent}{content}")
                else:
                    formatted_lines.append(line)

            return FormatterResult(success=True, content="\n".join(formatted_lines))
        except Exception as e:
            return FormatterResult(success=False, content=code, error=str(e))


class LanguageProviderRegistry:
    """Registry maintaining active language providers instances mapping."""

    def __init__(self) -> None:
        self._providers: Dict[str, LanguageProvider] = {}
        # Register default Python provider
        self.register(PythonLanguageProvider())

    def register(self, provider: LanguageProvider) -> None:
        self._providers[provider.get_language().lower()] = provider

    def get_provider(self, language: str) -> Optional[LanguageProvider]:
        return self._providers.get(language.lower())


import re
from typing import Optional
