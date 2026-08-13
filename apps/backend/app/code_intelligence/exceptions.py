"""Code Intelligence Exception Hierarchy Module.

Defines domain-specific exception types for Nova AI Enterprise Document & Code Intelligence Engine.
"""

from typing import Any, Dict, Optional


class CodeIntelligenceError(Exception):
    """Base exception class for all Code Intelligence errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RepositoryScanError(CodeIntelligenceError):
    """Raised when scanning repository structure or manifests fails."""
    pass


class LanguageNotSupportedError(CodeIntelligenceError):
    """Raised when file extension or shebang language is unsupported."""
    pass


class ASTParseError(CodeIntelligenceError):
    """Raised when AST parsing fails on source code file."""
    pass


class SymbolIndexingError(CodeIntelligenceError):
    """Raised when symbol table indexing fails."""
    pass


class ArchitectureExtractionError(CodeIntelligenceError):
    """Raised when architecture pattern extraction fails."""
    pass


class APIExtractionError(CodeIntelligenceError):
    """Raised when API route extraction fails."""
    pass


class DatabaseExtractionError(CodeIntelligenceError):
    """Raised when ORM model or SQL database extraction fails."""
    pass


class CodeIntelligenceHealthError(CodeIntelligenceError):
    """Raised when code intelligence diagnostic health checks fail."""
    pass
