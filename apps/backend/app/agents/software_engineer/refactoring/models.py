"""Pydantic schemas representing refactoring plans, snapshots, metrics and preview reports.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RefactoringTask(BaseModel):
    """Single refactoring step within an execution plan."""

    id: str = Field(..., description="Unique task identifier.")
    action: str = Field(..., description="Action category (e.g. rename, extract, modernize).")
    target_file: str = Field(..., description="Relative path of file to modify.")
    instructions: str = Field(..., description="Specific instructions mapping AST adjustments.")
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must execute first.")
    status: str = Field("pending", description="Task lifecycle status.")


class RefactoringPlan(BaseModel):
    """Dependency-aware plan detailing steps to apply refactoring."""

    plan_id: str
    request_summary: str
    tasks: List[RefactoringTask] = Field(default_factory=list)
    estimated_risk: str = Field("low", description="Predicted risk index (low, medium, high).")
    affected_files: List[str] = Field(default_factory=list)


class RefactoringRequest(BaseModel):
    """Parameters sent to orchestrate a codebase refactoring run."""

    prompt: str = Field(..., description="Refactoring goals instructions.")
    file_path: Optional[str] = Field(None, description="Optional path to target file.")
    refactor_type: Optional[str] = Field(None, description="Type of refactoring operation.")
    model_override: Optional[str] = Field(None)
    temperature: float = Field(0.2)
    max_tokens: int = Field(4096)


class SnapshotInfo(BaseModel):
    """Workspace backup session details."""

    snapshot_id: str
    timestamp: float
    workspace_root: str
    backed_up_files: Dict[str, str] = Field(
        default_factory=dict, description="Map of relative file paths to backup hashes/paths."
    )


class RollbackResult(BaseModel):
    """Result status of restoring backup snapshots."""

    success: bool
    snapshot_id: str
    restored_files: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class DiffReport(BaseModel):
    """Diff block records for altered files."""

    file_path: str
    unified_diff: str = Field("", description="Unified diff content block.")
    added_lines: int = Field(0)
    removed_lines: int = Field(0)


class PatchReport(BaseModel):
    """Details regarding applied patches."""

    patch_id: str
    patch_content: str = Field(..., description="Unified patch file content.")
    affected_files: List[str] = Field(default_factory=list)


class ConflictReport(BaseModel):
    """Report outlining identifier or symbol collisions."""

    has_conflict: bool
    collisions: List[str] = Field(default_factory=list, description="Descriptions of clashed identifiers.")
    introduces_cycles: bool = Field(False)


class ValidationReport(BaseModel):
    """Checks compilation and project structural integrity."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class DependencyUpdateResult(BaseModel):
    """Details import links updated after renaming/restructuring."""

    success: bool
    updated_files: List[str] = Field(default_factory=list)
    unresolved_imports: List[str] = Field(default_factory=list)


class SymbolRenameResult(BaseModel):
    """Renaming references outcomes."""

    success: bool
    symbol_name: str
    new_name: str
    occurrences_replaced: int = Field(0)


class ExtractionResult(BaseModel):
    """Code block extraction reports."""

    success: bool
    extracted_name: str
    extracted_code: str
    origin_file: str
    target_file: str


class OptimizationResult(BaseModel):
    """Structural simplification optimizations outcome details."""

    success: bool
    simplified_nodes_count: int = Field(0)
    optimization_patterns: List[str] = Field(default_factory=list)


class ModernizationResult(BaseModel):
    """Upgraded legacy syntax definitions outcomes."""

    success: bool
    features_upgraded: List[str] = Field(default_factory=list)


class RefactoringMetrics(BaseModel):
    """Performance statistics representing active executions."""

    model_time: float = Field(0.0)
    total_duration: float = Field(0.0)
    complexity_delta: int = Field(0)


class RefactoringPreview(BaseModel):
    """Refactoring details proposed for execution preview."""

    plan: RefactoringPlan
    diffs: List[DiffReport] = Field(default_factory=list)
    conflicts: ConflictReport
    estimated_risk: str = Field("low")
    rollback_available: bool = Field(True)


class RefactoringStatistics(BaseModel):
    """Detailed completion metadata logs."""

    duration: float
    affected_files_count: int
    validation_status: str
    model_used: str


class RefactoringResult(BaseModel):
    """Consolidated code refactoring run results."""

    success: bool
    snapshot_id: Optional[str] = None
    preview: Optional[RefactoringPreview] = None
    applied_patches: Optional[PatchReport] = None
    statistics: RefactoringStatistics
    rollback_result: Optional[RollbackResult] = None


class RefactoringContext(BaseModel):
    """Code intelligence contexts used to construct prompts."""

    workspace_root: str
    target_file: Optional[str] = None
    symbol_definitions: List[str] = Field(default_factory=list)
    style_guidelines: Optional[Dict[str, Any]] = None
    dependency_graph_summary: Optional[Dict[str, Any]] = None


class RefactoringHistory(BaseModel):
    """List of previously completed refactor operations."""

    operations: List[Dict[str, Any]] = Field(default_factory=list)
