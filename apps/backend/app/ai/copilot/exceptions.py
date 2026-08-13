"""Custom exception hierarchy for AI Software Copilot.
"""


class CopilotError(Exception):
    """Base exception for all AI Software Copilot errors."""

    pass


class RequirementAnalysisError(CopilotError):
    """Raised when Requirement Analysis Engine fails to parse requirements."""

    pass


class ArchitectureGenerationError(CopilotError):
    """Raised when Software Architecture Engine fails to design architecture."""

    pass


class CodeGenerationError(CopilotError):
    """Raised when Code Generation Engine fails to produce source files."""

    pass


class DebuggingFailedError(CopilotError):
    """Raised when Debugging Engine cannot locate root cause or apply fix."""

    pass


class RefactoringFailedError(CopilotError):
    """Raised when Refactoring Engine fails to transform code safely."""

    pass


class TestExecutionError(CopilotError):
    """Raised when Test Engine fails to execute or suite fails critical checks."""

    pass


class DeploymentError(CopilotError):
    """Raised when DevOps Engine encounters error generating container/pipeline configs."""

    pass
