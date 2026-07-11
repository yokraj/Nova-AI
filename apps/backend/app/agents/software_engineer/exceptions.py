"""Exceptions specific to the Software Engineering Agent.
"""

from app.agent_sdk.exceptions import SDKRuntimeError


class SoftwareEngineerError(SDKRuntimeError):
    """Base exception for all Software Engineering Agent errors."""

    pass


class WorkspaceError(SoftwareEngineerError):
    """Raised when workspace setup or access validation fails."""

    pass


class RepositoryError(SoftwareEngineerError):
    """Raised when repository indexing or checks fail."""

    pass


class CodeAnalysisError(SoftwareEngineerError):
    """Raised when code analysis or parsing fails."""

    pass


class ConfigurationError(SoftwareEngineerError):
    """Raised when agent configurations validate failed."""

    pass


class SessionError(SoftwareEngineerError):
    """Raised when session tracking updates fail."""

    pass
