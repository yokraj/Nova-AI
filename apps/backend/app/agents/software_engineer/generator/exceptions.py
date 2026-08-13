"""Custom exceptions for the Code Generation Engine.
"""

from app.agents.software_engineer.exceptions import SoftwareEngineerError


class CodeGenerationError(SoftwareEngineerError):
    """Base exception for all code generation errors."""

    pass


class PromptGenerationError(CodeGenerationError):
    """Raised when prompt construction or template filling fails."""

    pass


class TemplateError(CodeGenerationError):
    """Raised when loading or rendering code templates fails."""

    pass


class ValidationError(CodeGenerationError):
    """Raised when generated code validation fails."""

    pass


class FormattingError(CodeGenerationError):
    """Raised when formatting generated code fails."""

    pass


class ContextBuildError(CodeGenerationError):
    """Raised when building code generation context logs fails."""

    pass


class StyleAnalysisError(CodeGenerationError):
    """Raised when codebase style scanning fails."""

    pass


class UnsupportedLanguageError(CodeGenerationError):
    """Raised when requesting generation for an unsupported programming language."""

    pass


class ModelGenerationError(CodeGenerationError):
    """Raised when local AI model generation invocation fails."""

    pass


class PostProcessingError(CodeGenerationError):
    """Raised when merging or post-processing generated code outputs fails."""

    pass
