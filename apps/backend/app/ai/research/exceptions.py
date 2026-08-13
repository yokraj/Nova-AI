"""Custom exception hierarchy for Universal Knowledge, Research & Reasoning Engine.
"""


class ResearchEngineError(Exception):
    """Base exception for all Research Engine errors."""

    pass


class SearchFailedError(ResearchEngineError):
    """Raised when search query execution fails."""

    pass


class VerificationFailedError(ResearchEngineError):
    """Raised when evidence verification cross-checking fails."""

    pass


class DocumentParsingFailedError(ResearchEngineError):
    """Raised when document intelligence parsing fails."""

    pass


class GraphError(ResearchEngineError):
    """Raised when Knowledge Graph operation encounters an error."""

    pass


class ReportGenerationFailedError(ResearchEngineError):
    """Raised when synthesizing final research report fails."""

    pass
