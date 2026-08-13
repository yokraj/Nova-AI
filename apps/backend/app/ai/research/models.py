"""Pydantic data models, enums, and structures for Universal Knowledge, Research & Reasoning Engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class ResearchState(str, Enum):
    """Enumerate research workflow execution states."""

    CREATED = "CREATED"
    PLANNING = "PLANNING"
    COLLECTING = "COLLECTING"
    VERIFYING = "VERIFYING"
    REASONING = "REASONING"
    GENERATING_REPORT = "GENERATING_REPORT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RESUMED = "RESUMED"


class ResearchMode(str, Enum):
    """Enumerate research execution modes."""

    FAST = "fast"
    DEEP = "deep"
    AUTONOMOUS = "autonomous"
    RECURSIVE = "recursive"
    CONTINUOUS = "continuous"


class SourceType(str, Enum):
    """Enumerate knowledge source categories."""

    LOCAL_FILE = "local_file"
    WEB_PAGE = "web_page"
    REPOSITORY = "repository"
    DOCUMENT = "document"
    PDF = "pdf"
    OCR_IMAGE = "ocr_image"
    API = "api"
    MEMORY = "memory"
    MISSION = "mission"


class EvidenceLevel(str, Enum):
    """Enumerate evidence claim support levels."""

    DIRECT_FACT = "direct_fact"
    SUPPORTING_CLAIM = "supporting_claim"
    CONFLICTING_CLAIM = "conflicting_claim"
    UNCERTAIN = "uncertain"
    SPECULATION = "speculation"


class KnowledgeType(str, Enum):
    """Enumerate Knowledge Graph entity types."""

    CONCEPT = "concept"
    TECHNOLOGY = "technology"
    REPOSITORY = "repository"
    COMPANY = "company"
    PERSON = "person"
    PROJECT = "project"
    API_REF = "api_ref"


class ConfidenceLevel(str, Enum):
    """Enumerate claim confidence scores."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNVERIFIED = "UNVERIFIED"


class ReportType(str, Enum):
    """Enumerate research report format types."""

    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_REPORT = "technical_report"
    RESEARCH_REPORT = "research_report"
    COMPARISON_REPORT = "comparison_report"
    ARCHITECTURE_REPORT = "architecture_report"
    PRESENTATION_OUTLINE = "presentation_outline"
    VOICE_SUMMARY = "voice_summary"
    DEVELOPER_NOTES = "developer_notes"


class ResearchStatus(str, Enum):
    """Enumerate research session statuses."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class SubQuestion(BaseModel):
    """Decomposed sub-question in a research plan."""

    question_id: str = Field(default_factory=lambda: f"sq_{uuid.uuid4().hex[:8]}")
    query: str = Field(...)
    category: str = Field("general")
    required_sources: List[SourceType] = Field(default_factory=list)
    estimated_time_sec: float = Field(60.0)


class SearchStrategy(BaseModel):
    """Search execution strategy definition."""

    strategy_id: str = Field(default_factory=lambda: f"strat_{uuid.uuid4().hex[:8]}")
    primary_sources: List[SourceType] = Field(default_factory=list)
    use_browser: bool = Field(True)
    max_depth: int = Field(2)
    keywords: List[str] = Field(default_factory=list)


class ResearchPlan(BaseModel):
    """Structured execution plan for research inquiry."""

    plan_id: str = Field(default_factory=lambda: f"rplan_{uuid.uuid4().hex[:8]}")
    topic: str = Field(...)
    goals: List[str] = Field(default_factory=list)
    sub_questions: List[SubQuestion] = Field(default_factory=list)
    strategy: SearchStrategy = Field(default_factory=SearchStrategy)
    estimated_time_sec: float = Field(300.0)
    complexity: str = Field("medium")


class KnowledgeSource(BaseModel):
    """Ingested knowledge source descriptor."""

    source_id: str = Field(default_factory=lambda: f"src_{uuid.uuid4().hex[:8]}")
    title: str = Field(...)
    url_or_path: str = Field(...)
    type: SourceType = Field(SourceType.LOCAL_FILE)
    trust_score: float = Field(0.9)
    extracted_text: str = Field("")
    author: Optional[str] = Field(None)
    publication_date: Optional[str] = Field(None)


class ClaimVerification(BaseModel):
    """Verified claim statement with evidence cross-validation."""

    claim_id: str = Field(default_factory=lambda: f"clm_{uuid.uuid4().hex[:8]}")
    statement: str = Field(...)
    evidence_level: EvidenceLevel = Field(EvidenceLevel.DIRECT_FACT)
    confidence: ConfidenceLevel = Field(ConfidenceLevel.HIGH)
    supporting_sources: List[str] = Field(default_factory=list)
    conflicting_sources: List[str] = Field(default_factory=list)
    verification_score: float = Field(0.95)


class KnowledgeGraphNode(BaseModel):
    """Entity node in local Knowledge Graph."""

    node_id: str = Field(...)
    label: str = Field(...)
    type: KnowledgeType = Field(KnowledgeType.CONCEPT)
    properties: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphEdge(BaseModel):
    """Directed edge in local Knowledge Graph."""

    edge_id: str = Field(default_factory=lambda: f"edge_{uuid.uuid4().hex[:8]}")
    source_id: str = Field(...)
    target_id: str = Field(...)
    relation: str = Field("uses")
    weight: float = Field(1.0)


class RepositorySummary(BaseModel):
    """Repository Intelligence structure."""

    repo_path: str = Field(...)
    name: str = Field(...)
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    architecture_pattern: str = Field("Modular")
    module_structure: Dict[str, Any] = Field(default_factory=dict)
    summary: str = Field("")


class DocumentAnalysis(BaseModel):
    """Document Intelligence structure."""

    doc_path: str = Field(...)
    title: str = Field(...)
    page_count: int = Field(1)
    format: str = Field("PDF")
    paragraphs: List[str] = Field(default_factory=list)
    tables: List[List[List[str]]] = Field(default_factory=list)
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = Field("")


class CitationItem(BaseModel):
    """Formatted academic/reference citation."""

    citation_id: str = Field(default_factory=lambda: f"cite_{uuid.uuid4().hex[:8]}")
    source_title: str = Field(...)
    url_or_path: str = Field(...)
    author: str = Field("Nova Researcher")
    year: int = Field(2026)
    citation_string: str = Field("")


class ResearchReport(BaseModel):
    """Complete research synthesis report."""

    report_id: str = Field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:8]}")
    topic: str = Field(...)
    report_type: ReportType = Field(ReportType.TECHNICAL_REPORT)
    executive_summary: str = Field("")
    technical_details: str = Field("")
    comparisons: List[Dict[str, Any]] = Field(default_factory=list)
    voice_summary: str = Field("")
    citations: List[CitationItem] = Field(default_factory=list)


class KnowledgePackage(BaseModel):
    """Reusable structured knowledge package."""

    package_id: str = Field(default_factory=lambda: f"pkg_{uuid.uuid4().hex[:8]}")
    topic: str = Field(...)
    documentation: str = Field("")
    examples: List[str] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    common_errors: List[str] = Field(default_factory=list)
    api_reference: Dict[str, Any] = Field(default_factory=dict)


class ReasoningOutput(BaseModel):
    """Structured conclusion output from Reasoning Engine."""

    topic: str = Field(...)
    conclusions: List[str] = Field(default_factory=list)
    evidence_summary: str = Field("")
    uncertainties: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)


class ResearchMemoryItem(BaseModel):
    """Research session memory record."""

    item_id: str = Field(default_factory=lambda: f"rmem_{uuid.uuid4().hex[:8]}")
    topic: str = Field(...)
    plan: ResearchPlan = Field(...)
    report: ResearchReport = Field(...)
    citations_count: int = Field(0)
    timestamp: float = Field(default_factory=time.time)


class ResearchMetrics(BaseModel):
    """Telemetry collector metrics model."""

    queries_processed: int = Field(0)
    sources_ingested: int = Field(0)
    claims_verified: int = Field(0)
    reports_generated: int = Field(0)
    avg_time_sec: float = Field(0.0)
    timestamp: float = Field(default_factory=time.time)


class ResearchHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    research_state: ResearchState = Field(ResearchState.CREATED)
    graph_nodes_count: int = Field(0)
    graph_edges_count: int = Field(0)
    timestamp: float = Field(default_factory=time.time)
