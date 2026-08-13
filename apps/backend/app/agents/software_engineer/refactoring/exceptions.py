"""Domain exceptions for the Refactoring Engine.
"""

from app.agents.software_engineer.exceptions import SoftwareEngineerError


class RefactoringError(SoftwareEngineerError):
    """Base exception for all refactoring-related operations."""

    pass


class TransformationError(RefactoringError):
    """Raised when applying AST changes fails."""

    pass


class RenameConflictError(RefactoringError):
    """Raised when renaming causes identifier clashes."""

    pass


class ExtractionError(RefactoringError):
    """Raised when extracting code elements fails."""

    pass


class ModernizationError(RefactoringError):
    """Raised when upgrading legacy syntax fails."""

    pass


class OptimizationError(RefactoringError):
    """Raised when code structure simplifications fail."""

    pass


class ValidationFailureError(RefactoringError):
    """Raised when pre- or post-refactoring checks fail."""

    pass


class RollbackError(RefactoringError):
    """Raised when restoring snapshot content fails."""

    pass


class SnapshotError(RefactoringError):
    """Raised when writing backup snapshots fails."""

    pass


class DiffGenerationError(RefactoringError):
    """Raised when compiling code differences logs fails."""

    pass


class PatchGenerationError(RefactoringError):
    """Raised when generating unified patch files fails."""

    pass


class ConflictDetectionError(RefactoringError):
    """Raised when static checks find pre-existing or introduced merge conflicts."""

    pass


class DependencyUpdateError(RefactoringError):
    """Raised when updating file import links or referencing paths fails."""

    pass


class ImportResolutionError(RefactoringError):
    """Raised when import management resolves module paths incorrectly."""

    pass


class PreviewGenerationError(RefactoringError):
    """Raised when preview calculations fail."""

    pass
