"""Abstract interfaces defining Refactoring Engine component boundaries.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.refactoring.models import (
    ConflictReport,
    DependencyUpdateResult,
    DiffReport,
    ExtractionResult,
    ModernizationResult,
    OptimizationResult,
    PatchReport,
    RefactoringContext,
    RefactoringPlan,
    RefactoringPreview,
    RefactoringRequest,
    RefactoringResult,
    RollbackResult,
    SnapshotInfo,
    SymbolRenameResult,
    ValidationReport,
)
from app.agents.software_engineer.generator.models import FormatterResult, StyleProfile, PromptPackage


class RefactoringPlanner(ABC):
    """Decomposes refactoring requests into execution step task lists."""

    @abstractmethod
    def plan_refactoring(
        self, request: RefactoringRequest, context: RefactoringContext
    ) -> RefactoringPlan:
        """Parses requests and compiles dependency-aware RefactoringPlans."""
        pass


class RefactoringAnalyzer(ABC):
    """Analyzes codebase modules to identify refactoring opportunities and code smells."""

    @abstractmethod
    def identify_opportunities(self, workspace_path: str) -> List[Dict[str, Any]]:
        """Walks target workspace scanning for duplicate logic or complex functions."""
        pass


class CodeTransformer(ABC):
    """Performs safe syntax AST adjustments on python files."""

    @abstractmethod
    def transform_ast(self, file_path: str, transformer_node: Any) -> str:
        """Applies node modifications and regenerates source code."""
        pass


class SymbolRenamer(ABC):
    """Renames variables, class structures, or modules, updating all workspace usages."""

    @abstractmethod
    def rename_symbol(
        self, workspace_path: str, file_path: str, old_name: str, new_name: str
    ) -> SymbolRenameResult:
        """Project-wide rename of references to target symbol."""
        pass


class CodeExtractor(ABC):
    """Extracts helpers or inline methods, rewriting calls paths."""

    @abstractmethod
    def extract_symbol(
        self, file_path: str, target_node: Any, output_name: str
    ) -> ExtractionResult:
        """Splits code scopes to pull helper routines."""
        pass


class CodeModernizer(ABC):
    """Upgrades legacy syntax constructs (e.g. types, formats)."""

    @abstractmethod
    def modernize_code(self, code: str) -> ModernizationResult:
        """Converts deprecated syntax representations."""
        pass


class CodeOptimizer(ABC):
    """Simplifies complex conditionals or loop nesting constructs."""

    @abstractmethod
    def optimize_code(self, code: str) -> OptimizationResult:
        """Applies logic simplifications."""
        pass


class ImportManager(ABC):
    """Resolves unused imports or reorganizes absolute/relative imports."""

    @abstractmethod
    def clean_imports(self, file_path: str, code: str) -> str:
        """Sorts and prunes import paths."""
        pass


class DependencyUpdater(ABC):
    """Updates internal references after class/module transfers."""

    @abstractmethod
    def update_dependencies(
        self, workspace_path: str, affected_files: List[str]
    ) -> DependencyUpdateResult:
        """Ensures project links remain integral."""
        pass


class Formatter(ABC):
    """Formats refactored outputs matching StyleProfile layout rules."""

    @abstractmethod
    def format_code(self, code: str, style: StyleProfile) -> FormatterResult:
        """Enforces spacing conventions."""
        pass


class Validator(ABC):
    """Runs compiler and structure checks on refactored outputs."""

    @abstractmethod
    def validate_code(self, file_path: str, code: str) -> ValidationReport:
        """Performs syntax validation compiling checks."""
        pass


class RollbackManager(ABC):
    """Restores workspace target files state from snapshot records."""

    @abstractmethod
    def rollback(self, snapshot_id: str) -> RollbackResult:
        """Restores original file configurations."""
        pass


class SnapshotManager(ABC):
    """Creates local directory state backups before code changes are applied."""

    @abstractmethod
    def create_snapshot(
        self, workspace_path: str, file_paths: List[str]
    ) -> SnapshotInfo:
        """Copies file backups to snapshots storage."""
        pass


class DiffGenerator(ABC):
    """Compiles line-by-line unified diff changes logs."""

    @abstractmethod
    def generate_diff(self, file_path: str, original: str, modified: str) -> DiffReport:
        """Compares string states and returns diff logs."""
        pass


class PatchGenerator(ABC):
    """Compiles standard patch files matching applied operations."""

    @abstractmethod
    def generate_patch(self, diffs: List[DiffReport]) -> PatchReport:
        """Builds unified patch strings."""
        pass


class PreviewProvider(ABC):
    """Assembles proposed changes into a read-only inspectable preview."""

    @abstractmethod
    def generate_preview(
        self, request: RefactoringRequest, context: RefactoringContext
    ) -> RefactoringPreview:
        """Generates risk, conflict, and diff reports preview."""
        pass


class ConflictDetector(ABC):
    """Validates if refactoring introduces cycles or symbol clashes."""

    @abstractmethod
    def detect_conflicts(
        self, workspace_path: str, plan: RefactoringPlan
    ) -> ConflictReport:
        """Pre-refactor verification scan checking for clashes."""
        pass


class ContextBuilder(ABC):
    """Builds refactoring query context."""

    @abstractmethod
    def build_context(
        self, request: RefactoringRequest, workspace_path: str
    ) -> RefactoringContext:
        """Gathers codebase graphs and constraints."""
        pass


class PromptBuilder(ABC):
    """Constructs instructions prompts mapping goals to LLMs."""

    @abstractmethod
    def build_prompt(
        self, request: RefactoringRequest, context: RefactoringContext, instructions: str
    ) -> PromptPackage:
        """Builds prompt messages package."""
        pass


class RefactoringEngine(ABC):
    """Core Refactoring Engine interface coordinating execution runs."""

    @abstractmethod
    async def execute_refactoring(self, request: RefactoringRequest) -> RefactoringResult:
        """Orchestrates snapshotting, model chat prompts, validation, formatting, and patches."""
        pass
