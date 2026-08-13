"""Abstract interfaces outlining boundaries for all documentation components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.documentation.models import (
    APIDocument,
    ArchitectureDocument,
    CodeDocument,
    DocumentationContext,
    DocumentationPlan,
    DocumentationReport,
    DocumentationRequest,
    DocumentationVersion,
    KnowledgeEntry,
    KnowledgeIndex,
    ReadmeDocument,
    SyncResult,
)
from app.agents.software_engineer.generator.models import PromptPackage


class DocumentationPlanner(ABC):
    """Decomposes documentation request goals prioritizing undocumented modules."""

    @abstractmethod
    def plan_documentation(
        self, request: DocumentationRequest, context: DocumentationContext
    ) -> DocumentationPlan:
        """Formulates checklist of documentation tasks."""
        pass


class ContextBuilder(ABC):
    """Gathers repository statistics and active styling configurations."""

    @abstractmethod
    def build_context(
        self, request: DocumentationRequest, workspace_path: str
    ) -> DocumentationContext:
        """Assembles file count, language footprint stats, and style settings."""
        pass


class PromptBuilder(ABC):
    """Constructs prompt message package instructing active local coding models."""

    @abstractmethod
    def build_prompt(
        self, request: DocumentationRequest, context: DocumentationContext, task_instructions: str
    ) -> PromptPackage:
        """Packages instructions for generating documentation."""
        pass


class CodeDocumenter(ABC):
    """Generates detailed code level documentation logs."""

    @abstractmethod
    def document_code(
        self, workspace_path: str, file_path: str
    ) -> CodeDocument:
        """Parses files generating class and function documentation blocks."""
        pass


class ArchitectureGenerator(ABC):
    """Generates high level structural system design logs."""

    @abstractmethod
    def generate_architecture(
        self, workspace_path: str
    ) -> ArchitectureDocument:
        """Analyzes directory tree mapping components and relationships."""
        pass


class APIDocumenter(ABC):
    """Documents FastAPI routing controllers and request schemas."""

    @abstractmethod
    def document_api(
        self, workspace_path: str, file_path: str
    ) -> List[APIDocument]:
        """Statically processes routes matching signatures."""
        pass


class DiagramGenerator(ABC):
    """Generates visual Mermaid code blocks representing workflows."""

    @abstractmethod
    def generate_diagram(
        self, diagram_type: str, context: Dict[str, Any]
    ) -> str:
        """Compiles structure arrays into Mermaid format strings."""
        pass


class KnowledgeBuilder(ABC):
    """Aggregates change logs and business rules into local knowledge cache entries."""

    @abstractmethod
    def build_knowledge(
        self, workspace_path: str
    ) -> List[KnowledgeEntry]:
        """Compiles index details."""
        pass


class KnowledgeIndexer(ABC):
    """Manages keyword and semantic search indexing."""

    @abstractmethod
    def index_knowledge(
        self, entries: List[KnowledgeEntry]
    ) -> KnowledgeIndex:
        """Indexes entries mapping title and terms."""
        pass


class DocumentationSync(ABC):
    """Identifies documentation files requiring updates matched with code modifications."""

    @abstractmethod
    def sync_documentation(
        self, workspace_path: str, modified_files: List[str]
    ) -> SyncResult:
        """Compares hashes identifying outdated modules."""
        pass


class VersionTracker(ABC):
    """Tracks document version histories and generated timestamps."""

    @abstractmethod
    def track_version(
        self, doc_type: str, file_path: str, content: str
    ) -> DocumentationVersion:
        """Increments version codes recording SHA hashes."""
        pass


class TemplateEngine(ABC):
    """Injects project parameters into predefined documentation layouts templates."""

    @abstractmethod
    def render_template(
        self, template_name: str, parameters: Dict[str, Any]
    ) -> str:
        """Fills placeholders with values parameters."""
        pass


class Renderer(ABC):
    """Formats markdown layouts into HTML pages or PDF binaries."""

    @abstractmethod
    def render_to_html(self, markdown_text: str) -> str:
        """Formats layout into HTML."""
        pass

    @abstractmethod
    def render_to_pdf(self, markdown_text: str) -> bytes:
        """Formats layout into PDF binary string."""
        pass


class ReportGenerator(ABC):
    """Generates documentation audits summary reports."""

    @abstractmethod
    def generate_report(
        self, plan: DocumentationPlan, report_text: str
    ) -> DocumentationReport:
        """Aggregates task list and outputs Markdown summaries."""
        pass


class DocumentationEngine(ABC):
    """Central orchestrator managing documentation planners, template engines, and renderers."""

    @abstractmethod
    async def execute_documentation_pipeline(
        self, request: DocumentationRequest
    ) -> DocumentationReport:
        """Orchestrates full analysis, generation, rendering, and caching pipeline."""
        pass
