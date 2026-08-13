"""Abstract base interfaces and contracts for Universal Knowledge, Research & Reasoning Engine components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.research.models import (
    CitationItem,
    ClaimVerification,
    DocumentAnalysis,
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    KnowledgePackage,
    KnowledgeSource,
    ReasoningOutput,
    RepositorySummary,
    ResearchHealth,
    ResearchMemoryItem,
    ResearchMetrics,
    ResearchPlan,
    ResearchReport,
)


class IResearchPlanner(ABC):
    """Research Planner contract generating sub-questions and execution plans."""

    @abstractmethod
    async def create_plan(self, topic: str, **kwargs: Any) -> ResearchPlan:
        """Decomposes research query into roadmap and sub-questions."""
        pass


class ISearchEngine(ABC):
    """Search Engine contract executing local and web inquiries."""

    @abstractmethod
    async def search(self, query: str, **kwargs: Any) -> List[KnowledgeSource]:
        """Searches local documents, knowledge base, browser, GitHub, and APIs."""
        pass


class IKnowledgeCollector(ABC):
    """Knowledge Collector contract ingesting multi-format sources."""

    @abstractmethod
    async def collect_knowledge(self, source_path_or_url: str) -> KnowledgeSource:
        """Ingests content from files, web pages, PDFs, repositories, and OCR images."""
        pass


class IVerificationEngine(ABC):
    """Evidence Verification Engine contract cross-checking claims."""

    @abstractmethod
    async def verify_claim(self, claim_statement: str, sources: List[KnowledgeSource]) -> ClaimVerification:
        """Cross-validates claim against evidence sources and scores confidence."""
        pass


class IReasoningEngine(ABC):
    """Reasoning Engine contract generating conclusions and inferring insights."""

    @abstractmethod
    async def reason(self, topic: str, claims: List[ClaimVerification]) -> ReasoningOutput:
        """Compares evidence, resolves conflicts, and generates conclusions."""
        pass


class IKnowledgeGraph(ABC):
    """Local Knowledge Graph contract managing entities and relations."""

    @abstractmethod
    def add_node(self, node: KnowledgeGraphNode) -> None:
        """Adds node to graph."""
        pass

    @abstractmethod
    def add_edge(self, edge: KnowledgeGraphEdge) -> None:
        """Adds directed relation edge to graph."""
        pass

    @abstractmethod
    def get_related_nodes(self, node_id: str) -> List[KnowledgeGraphNode]:
        """Traverses graph for connected entities."""
        pass


class IRepositoryAnalyzer(ABC):
    """Repository Analyzer contract parsing codebase architecture and dependencies."""

    @abstractmethod
    async def analyze_repository(self, repo_path: str) -> RepositorySummary:
        """Analyzes directory structure, frameworks, languages, build systems."""
        pass


class IDocumentIntelligence(ABC):
    """Document Intelligence contract parsing PDFs, Office docs, tables, charts."""

    @abstractmethod
    async def analyze_document(self, doc_path: str) -> DocumentAnalysis:
        """Parses document into structured paragraphs, tables, and summaries."""
        pass


class ICitationEngine(ABC):
    """Citation Engine contract generating formatted reference citations."""

    @abstractmethod
    def generate_citation(self, source: KnowledgeSource, style: str = "APA") -> CitationItem:
        """Formats citation item in specified style."""
        pass


class IReportGenerator(ABC):
    """Report Generator contract creating executive, technical, and voice reports."""

    @abstractmethod
    async def generate_report(self, topic: str, reasoning: ReasoningOutput, citations: List[CitationItem]) -> ResearchReport:
        """Synthesizes structured research report."""
        pass


class IResearchMemory(ABC):
    """Research Memory contract tracking historical research sessions."""

    @abstractmethod
    async def save_session(self, memory_item: ResearchMemoryItem) -> None:
        """Saves research session to memory."""
        pass

    @abstractmethod
    async def get_session(self, topic: str) -> Optional[ResearchMemoryItem]:
        """Retrieves past research session for incremental research resumption."""
        pass


class IResearchAgent(ABC):
    """Research Agent contract executing swarm research tasks."""

    @abstractmethod
    async def execute_research_task(self, task_description: str) -> Dict[str, Any]:
        """Performs specialized swarm research synthesis."""
        pass


class IResearchManager(ABC):
    """Research Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts research engine."""
        pass


class IResearchEngine(ABC):
    """Central Universal Research Engine facade contract."""

    @abstractmethod
    async def research(self, topic: str, **kwargs: Any) -> ResearchReport:
        """Performs end-to-end autonomous research and report synthesis."""
        pass

    @abstractmethod
    async def search(self, query: str, **kwargs: Any) -> List[KnowledgeSource]:
        """Searches local and external knowledge bases."""
        pass

    @abstractmethod
    async def analyze_document(self, doc_path: str) -> DocumentAnalysis:
        """Parses document into structured knowledge."""
        pass

    @abstractmethod
    async def analyze_repository(self, repo_path: str) -> RepositorySummary:
        """Analyzes repository code architecture and dependencies."""
        pass

    @abstractmethod
    async def generate_report(self, topic: str, **kwargs: Any) -> ResearchReport:
        """Generates structured report."""
        pass

    @abstractmethod
    async def knowledge_graph(self) -> Dict[str, Any]:
        """Retrieves local Knowledge Graph nodes and edges."""
        pass

    @abstractmethod
    async def citations(self) -> List[CitationItem]:
        """Retrieves active citations list."""
        pass

    @abstractmethod
    async def research_history(self) -> List[ResearchMemoryItem]:
        """Retrieves research session history."""
        pass

    @abstractmethod
    async def continue_research(self, topic: str, new_query: str) -> ResearchReport:
        """Resumes previous research session incrementally."""
        pass

    @abstractmethod
    async def knowledge_package(self, topic: str) -> KnowledgePackage:
        """Retrieves stored reusable Knowledge Package."""
        pass
