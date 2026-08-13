"""Formats generated source code matching target style guidelines.
"""

from app.agents.software_engineer.generator.interfaces import Formatter
from app.agents.software_engineer.generator.language_provider import LanguageProviderRegistry
from app.agents.software_engineer.generator.models import FormatterResult, StyleProfile


class SourceCodeFormatter(Formatter):
    """Formats code using language providers styling rules."""

    def __init__(self, registry: Optional[LanguageProviderRegistry] = None) -> None:
        self.registry = registry or LanguageProviderRegistry()

    def format_code(self, code: str, style: StyleProfile) -> FormatterResult:
        """Looks up the Python language provider and reformats the code.

        Args:
            code: Source code content.
            style: Workspace StyleProfile configuration.

        Returns:
            FormatterResult model containing formatted string.
        """
        # Hardcoded to python for initial provider integration
        provider = self.registry.get_provider("python")
        if not provider:
            return FormatterResult(success=True, content=code)

        return provider.format(code, style)


from typing import Optional
