"""Interfaces outlining abstract boundaries for Code Generation components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.generator.models import (
    ContextSummary,
    FormatterResult,
    GenerationContext,
    GenerationPlan,
    GenerationRequest,
    GenerationResult,
    PromptPackage,
    StyleProfile,
    ValidationResult,
)


class GenerationPlanner(ABC):
    """Decomposes generation requests into multi-task dependencies generation plans."""

    @abstractmethod
    def plan_generation(
        self, request: GenerationRequest, context: GenerationContext
    ) -> GenerationPlan:
        """Decomposes the generation request into dependent tasks."""
        pass


class ContextBuilder(ABC):
    """Collects repository metadata and file logs to construct prompts context summaries."""

    @abstractmethod
    def build_context(
        self, request: GenerationRequest, workspace_path: str
    ) -> GenerationContext:
        """Assembles symbols, style guides, and related files into context."""
        pass


class PromptBuilder(ABC):
    """Orchestrates system constraints and codebase snippets to compile LLM instructions."""

    @abstractmethod
    def build_prompt(
        self, request: GenerationRequest, context: GenerationContext, task_instructions: str
    ) -> PromptPackage:
        """Builds system and user prompt messages package."""
        pass


class StyleAnalyzer(ABC):
    """Scans existing project files to extract style and format parameters."""

    @abstractmethod
    def analyze_style(self, workspace_path: str) -> StyleProfile:
        """Scans workspace python files to extract coding styles."""
        pass


class TemplateEngine(ABC):
    """Handles rendering standard code skeletons."""

    @abstractmethod
    def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Renders code string using template parameters."""
        pass


class CodeValidator(ABC):
    """Performs static syntax and structure tests on generated code."""

    @abstractmethod
    def validate_code(self, file_path: str, code: str) -> ValidationResult:
        """Statically compiles and tests generated code snippet."""
        pass


class Formatter(ABC):
    """Formats generated code using style rules configurations."""

    @abstractmethod
    def format_code(self, code: str, style: StyleProfile) -> FormatterResult:
        """Formats code snippet matching target style standards."""
        pass


class LanguageProvider(ABC):
    """Language-specific compiler hooks, validators and formatter hooks provider."""

    @abstractmethod
    def get_language(self) -> str:
        """Returns language identifier."""
        pass

    @abstractmethod
    def validate(self, file_path: str, code: str) -> ValidationResult:
        """Runs language syntax validation checks."""
        pass

    @abstractmethod
    def format(self, code: str, style: StyleProfile) -> FormatterResult:
        """Formats code matching language standards."""
        pass


class CodeGenerator(ABC):
    """Main Orchestrator API abstraction for Code Generation Engine."""

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Orchestrates full code generation pipeline returning generation result."""
        pass
