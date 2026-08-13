"""Custom exceptions for the Repository Analyzer module.
"""

from app.agents.software_engineer.exceptions import RepositoryError


class RepositoryException(RepositoryError):
    """Base exception for all repository analyzer errors."""

    pass


class RepositoryNotFoundError(RepositoryException):
    """Raised when the specified repository root is not found."""

    pass


class RepositoryScanError(RepositoryException):
    """Raised when an error occurs during repository scanning."""

    pass


class RepositoryCacheError(RepositoryException):
    """Raised when cache operations fail."""

    pass


class RepositoryIndexError(RepositoryException):
    """Raised when search or lookup operations on indexes fail."""

    pass


class UnsupportedRepositoryError(RepositoryException):
    """Raised when repository layout is not supported."""

    pass


class InvalidRepositoryError(RepositoryException):
    """Raised when workspace validation fails."""

    pass
