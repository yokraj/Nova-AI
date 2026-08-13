"""Custom exceptions for the Code Intelligence Engine.
"""

from app.agents.software_engineer.exceptions import SoftwareEngineerError


class CodeIntelligenceError(SoftwareEngineerError):
    """Base exception for all code intelligence engine errors."""

    pass


class ASTParsingError(CodeIntelligenceError):
    """Raised when parsing source code into AST fails."""

    pass


class SymbolResolutionError(CodeIntelligenceError):
    """Raised when resolving or indexing symbols fails."""

    pass


class DependencyAnalysisError(CodeIntelligenceError):
    """Raised when dependency or import analysis fails."""

    pass


class ComplexityAnalysisError(CodeIntelligenceError):
    """Raised when calculating cyclomatic or cognitive complexity fails."""

    pass


class DuplicateDetectionError(CodeIntelligenceError):
    """Raised when duplicated code analysis fails."""

    pass


class SemanticSearchError(CodeIntelligenceError):
    """Raised during search indexing or lookup execution errors."""

    pass


class CacheCorruptionError(CodeIntelligenceError):
    """Raised when loading or saving code intelligence cache fails."""

    pass


class UnsupportedLanguageError(CodeIntelligenceError):
    """Raised when requesting code analysis for an unsupported programming language."""

    pass
