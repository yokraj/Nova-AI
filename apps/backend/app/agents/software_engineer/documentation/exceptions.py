"""Custom domain exceptions for the Documentation & Knowledge Generation Engine.
"""


class DocumentationError(Exception):
    """Base exception for all documentation package issues."""
    pass


class GenerationError(DocumentationError):
    """Raised when documentation content generation fails."""
    pass


class TemplateError(DocumentationError):
    """Raised when documentation skeleton templates rendering fails."""
    pass


class RenderingError(DocumentationError):
    """Raised when formatting or converting layout to HTML or PDF fails."""
    pass


class SyncError(DocumentationError):
    """Raised when checking or syncing documentation with code files changes fails."""
    pass


class VersionError(DocumentationError):
    """Raised when tracking documentation version numbers fails."""
    pass


class KnowledgeError(DocumentationError):
    """Raised when loading or writing to local knowledge database fails."""
    pass


class IndexingError(DocumentationError):
    """Raised when indexing files or concepts details fails."""
    pass


class DiagramGenerationError(DocumentationError):
    """Raised when compiling Mermaid or PlantUML structures fails."""
    pass


class ValidationError(DocumentationError):
    """Raised when generated documentation validation fails."""
    pass
