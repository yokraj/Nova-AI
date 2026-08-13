"""Validates generated code syntax using language providers.
"""

from app.agents.software_engineer.generator.interfaces import CodeValidator
from app.agents.software_engineer.generator.language_provider import LanguageProviderRegistry
from app.agents.software_engineer.generator.models import ValidationResult


class GeneratedCodeValidator(CodeValidator):
    """Orchestrates language providers to validate generated code syntax."""

    def __init__(self, registry: Optional[LanguageProviderRegistry] = None) -> None:
        self.registry = registry or LanguageProviderRegistry()

    def validate_code(self, file_path: str, code: str) -> ValidationResult:
        """Determines target language provider and performs syntax checks.

        Args:
            file_path: Relative target file path.
            code: Source code content.

        Returns:
            ValidationResult payload.
        """
        # Determine language based on file extension
        ext = os.path.splitext(file_path)[1].lower()
        lang = "python"
        if ext in (".ts", ".tsx"):
            lang = "typescript"
        elif ext in (".js", ".jsx"):
            lang = "javascript"
        elif ext == ".go":
            lang = "go"
        elif ext == ".rs":
            lang = "rust"
        elif ext == ".java":
            lang = "java"

        provider = self.registry.get_provider(lang)
        if not provider:
            # Fallback check for python or allow validation to pass if unsupported
            return ValidationResult(is_valid=True)

        return provider.validate(file_path, code)


import os
from typing import Optional
