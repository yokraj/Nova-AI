"""Pydantic v2 schemas representing documentation planning and rendering scopes.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentationRequest(BaseModel):
    """Parameters representing a documentation generation request."""

    prompt: str = Field(..., description="Details regarding what documentation targets to draft.")
    workspace_root: Optional[str] = Field(None)
    model_override: Optional[str] = Field(None)
    temperature: float = Field(0.2)
    max_tokens: int = Field(4096)


class DocumentationTask(BaseModel):
    """A single subtask to document a module, class, or API endpoint."""

    id: str
    target_name: str
    task_type: str = Field("code", description="code, api, architecture, readme, changelog")
    instructions: str
    dependencies: List[str] = Field(default_factory=list)
    status: str = Field("pending")


class DocumentationPlan(BaseModel):
    """Decomposition of documentation request into dependent tasks."""

    plan_id: str
    summary: str
    tasks: List[DocumentationTask] = Field(default_factory=list)
    risk_level: str = Field("low")


class DocumentationContext(BaseModel):
    """Workspace metadata compiled before generating files."""

    workspace_root: str
    scanned_files_count: int
    languages_percentages: Dict[str, float] = Field(default_factory=dict)
    active_symbols: List[str] = Field(default_factory=list)
    style_guidelines: Optional[Dict[str, Any]] = None


class ClassDocument(BaseModel):
    """Document summary for a target class."""

    name: str
    purpose: str
    methods: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None


class FunctionDocument(BaseModel):
    """Document summary for a target function or method."""

    name: str
    purpose: str
    parameters: List[str] = Field(default_factory=list)
    returns: Optional[str] = None
    exceptions: List[str] = Field(default_factory=list)


class ModuleDocument(BaseModel):
    """Document summary for a Python module file."""

    file_path: str
    purpose: str
    classes: List[ClassDocument] = Field(default_factory=list)
    functions: List[FunctionDocument] = Field(default_factory=list)


class CodeDocument(BaseModel):
    """Collection of code level documents."""

    modules: List[ModuleDocument] = Field(default_factory=list)


class APIDocument(BaseModel):
    """Documentation representing REST/FastAPI endpoints."""

    endpoint: str
    method: str
    request_schema: Optional[str] = None
    response_schema: Optional[str] = None
    auth_required: bool = Field(False)
    description: Optional[str] = None


class ArchitectureDocument(BaseModel):
    """High level system architecture layout description."""

    components: List[str] = Field(default_factory=list)
    relationships: Dict[str, List[str]] = Field(default_factory=dict)
    mermaid_diagram: Optional[str] = None


class ReadmeDocument(BaseModel):
    """Markdown schema configuration representing standard README elements."""

    overview: str
    installation: str
    configuration: str
    usage: str


class ChangelogDocument(BaseModel):
    """Tracked code modification revisions mapped to semantic version changes."""

    version: str
    release_date: str
    features: List[str] = Field(default_factory=list)
    bug_fixes: List[str] = Field(default_factory=list)
    breaking_changes: List[str] = Field(default_factory=list)


class MigrationDocument(BaseModel):
    """Details mapping database changes or code deprecations steps."""

    target: str
    migration_steps: List[str] = Field(default_factory=list)
    breaking_changes: List[str] = Field(default_factory=list)


class DiagramDocument(BaseModel):
    """Mermaid code definitions representing structures layout."""

    diagram_type: str = Field(..., description="sequence, flow, class, dependency")
    code: str


class KnowledgeEntry(BaseModel):
    """Local cache entry mapping concepts descriptions."""

    title: str
    content: str
    category: str = Field("architecture", description="architecture, workflows, business_rules")
    timestamp: float


class KnowledgeIndex(BaseModel):
    """Collection of mapped knowledge entities."""

    entries: Dict[str, KnowledgeEntry] = Field(default_factory=dict)


class DocumentationVersion(BaseModel):
    """Tracking fields representing generated doc versions."""

    version_id: str
    doc_type: str
    file_path: str
    hash_value: str
    timestamp: float


class DocumentationChange(BaseModel):
    """A detected file change requiring document updates."""

    file_path: str
    symbol_name: Optional[str] = None
    change_type: str = Field(..., description="added, modified, deleted")


class SyncResult(BaseModel):
    """Synchronisation audit checking what documentation targets need updates."""

    outdated_docs: List[str] = Field(default_factory=list)
    changes: List[DocumentationChange] = Field(default_factory=list)


class DocumentationReport(BaseModel):
    """Final audit report compiling workspace document qualities."""

    overall_completeness: float = Field(0.0)
    undocumented_symbols: List[str] = Field(default_factory=list)
    plan: Optional[DocumentationPlan] = None
    generated_files: List[str] = Field(default_factory=list)
    report_markdown: str
