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
    SCHOLARLY_SOURCE = "scholarly_source"
    PASSAGE = "passage"
    CLAIM = "claim"
    VERIFICATION = "verification"


class ConfidenceLevel(str, Enum):
    """Enumerate claim confidence scores."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNVERIFIED = "UNVERIFIED"
    UNCERTAIN = "UNCERTAIN"


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
    line_count: int = Field(0)
    size_bytes: int = Field(0)
    ast_symbols: Optional[Dict[str, Any]] = Field(default=None)
    error: Optional[str] = Field(default=None)


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


class ScholarlyProviderStatus(str, Enum):
    """Execution status for scholarly metadata provider."""

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    RATE_LIMITED = "RATE_LIMITED"
    NO_RESULTS = "NO_RESULTS"


class ScholarlySourceRecord(BaseModel):
    """Normalized scholarly source record containing provenance and field validation metadata."""

    source_id: str = Field(default_factory=lambda: f"scholarly_{uuid.uuid4().hex[:12]}")
    title: str = Field(...)
    authors: List[str] = Field(default_factory=list)
    publication_year: Optional[int] = Field(None)
    doi: Optional[str] = Field(None)
    canonical_url: Optional[str] = Field(None)
    abstract: Optional[str] = Field(None)
    venue: Optional[str] = Field(None)
    provider: str = Field("unknown")
    retrieval_timestamp: float = Field(default_factory=time.time)
    retrieved_fields: List[str] = Field(default_factory=list)
    source_record_url: Optional[str] = Field(None)
    metadata_validation_status: str = Field("UNVERIFIED")
    full_text_status: str = Field("UNAVAILABLE")
    full_text_url: Optional[str] = Field(None)
    raw_provider_id: Optional[str] = Field(None)
    raw_metadata: Optional[Dict[str, Any]] = Field(None)
    is_untrusted_data: bool = Field(True)
    prompt_injection_flagged: bool = Field(False)
    contributing_providers: List[str] = Field(default_factory=list)
    provider_raw_ids: Dict[str, str] = Field(default_factory=dict)
    relevance_score: float = Field(0.0)
    match_type: str = Field("TOPIC_MATCH")
    match_explanation: str = Field("")


class DOIVerificationResult(BaseModel):
    """Result of syntactic validation, registry resolution, identity match, and metadata agreement check."""

    doi: str = Field(...)
    normalized_doi: Optional[str] = Field(None)
    is_syntactically_valid: bool = Field(False)
    is_resolved: bool = Field(False)
    returned_doi_match: bool = Field(False)
    resolved_title: Optional[str] = Field(None)
    resolved_authors: List[str] = Field(default_factory=list)
    resolved_year: Optional[int] = Field(None)
    resolved_url: Optional[str] = Field(None)
    title_agreement: str = Field("NOT_CHECKED")  # EXACT, SIMILAR, MISMATCH, NOT_CHECKED
    author_agreement: str = Field("NOT_CHECKED") # AGREED, PARTIAL, MISMATCH, NOT_CHECKED
    year_agreement: str = Field("NOT_CHECKED")   # AGREED, MISMATCH, NOT_CHECKED
    metadata_agreement: str = Field("UNRESOLVED") # Primary agreement field
    overall_metadata_agreement: str = Field("UNRESOLVED") # Explicit alias for overall agreement
    mismatch_details: List[str] = Field(default_factory=list)
    registry_provider: str = Field("none")
    verification_timestamp: float = Field(default_factory=time.time)


class LiteratureSearchResult(BaseModel):
    """Structured result of multi-provider literature search."""

    search_id: str = Field(default_factory=lambda: f"litsearch_{uuid.uuid4().hex[:8]}")
    query: str = Field(...)
    total_found: int = Field(0)
    deduplicated_count: int = Field(0)
    sources: List[ScholarlySourceRecord] = Field(default_factory=list)
    provider_statuses: Dict[str, ScholarlyProviderStatus] = Field(default_factory=dict)
    duration_sec: float = Field(0.0)
    executed_at: float = Field(default_factory=time.time)


class ClaimVerificationOutcome(str, Enum):
    """Enumerate evidence verification outcomes for claims (Phase 10L-B)."""

    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNVERIFIED_ASSUMPTION = "UNVERIFIED_ASSUMPTION"


class ClaimType(str, Enum):
    """Enumerate atomic claim categories (Phase 10L-B)."""

    DIRECT_STATEMENT = "direct_statement"
    DERIVED_INFERENCE = "derived_inference"
    NUMERIC_FINDING = "numeric_finding"
    METHODOLOGICAL_CLAIM = "methodological_claim"


class SourcePassage(BaseModel):
    """Exact extract of source text from a paper or document (Phase 10L-B)."""

    passage_id: str = Field(default_factory=lambda: f"psg_{uuid.uuid4().hex[:10]}")
    source_id: str = Field(...)
    text: str = Field(...)
    section: str = Field("abstract")
    char_offset_start: Optional[int] = Field(None)
    char_offset_end: Optional[int] = Field(None)
    is_untrusted_data: bool = Field(True)
    prompt_injection_flagged: bool = Field(False)
    extracted_at: float = Field(default_factory=time.time)


class AtomicClaim(BaseModel):
    """Atomic factual proposition extracted from or evaluated against source passages (Phase 10L-B)."""

    claim_id: str = Field(default_factory=lambda: f"clm_{uuid.uuid4().hex[:10]}")
    statement: str = Field(...)
    claim_type: ClaimType = Field(ClaimType.DIRECT_STATEMENT)
    source_passage_id: Optional[str] = Field(None)
    original_passage_text: Optional[str] = Field(None)
    extracted_numerical_values: List[str] = Field(default_factory=list)
    is_derived: bool = Field(False)
    confidence_score: float = Field(1.0)
    created_at: float = Field(default_factory=time.time)


class EvidenceRelation(BaseModel):
    """Directional relationship between a claim and supporting or contradicting source evidence (Phase 10L-B)."""

    relation_id: str = Field(default_factory=lambda: f"evrel_{uuid.uuid4().hex[:10]}")
    claim_id: str = Field(...)
    passage_id: Optional[str] = Field(None)
    source_id: Optional[str] = Field(None)
    outcome: ClaimVerificationOutcome = Field(ClaimVerificationOutcome.INSUFFICIENT_EVIDENCE)
    rationale: str = Field("")
    source_doi: Optional[str] = Field(None)
    source_url: Optional[str] = Field(None)
    source_title: Optional[str] = Field(None)
    publication_year: Optional[int] = Field(None)
    is_corroborated: bool = Field(False)
    contributing_providers: List[str] = Field(default_factory=list)


class ClaimVerificationDetail(BaseModel):
    """Structured verification evaluation for a specific atomic claim (Phase 10L-B)."""

    claim_id: str = Field(...)
    statement: str = Field(...)
    outcome: ClaimVerificationOutcome = Field(ClaimVerificationOutcome.UNVERIFIED_ASSUMPTION)
    supporting_passages: List[Dict[str, Any]] = Field(default_factory=list)
    contradicting_passages: List[Dict[str, Any]] = Field(default_factory=list)
    insufficient_passages: List[Dict[str, Any]] = Field(default_factory=list)
    independent_sources_count: int = Field(0)
    verification_explanation: str = Field("")
    is_orphan: bool = Field(False)


# =============================================================================
# Phase 10L-C: Evidence-Grounded Research Answer Synthesis Models
# =============================================================================

class ClaimEpistemicStatus(str, Enum):
    """Epistemic status of a claim in evidence-grounded research answer synthesis (Phase 10L-C)."""

    VERIFIED_FACT = "VERIFIED_FACT"        # Directly entailed by verified source passages
    INFERENCE = "INFERENCE"                # Derived deduction or hedged finding supported by evidence
    UNSUPPORTED = "UNSUPPORTED"            # Insufficient evidence or unverified assumption
    CONTRADICTED = "CONTRADICTED"          # Disputed / contradicted by source evidence


class SynthesisMode(str, Enum):
    """Synthesis operational mode (Phase 10L-C)."""

    GROUNDED_STRICT = "grounded_strict"    # Zero unsupported statements permitted as facts
    BALANCED = "balanced"                  # Permits derived inferences with explicit hedging
    EXPLORATORY = "exploratory"            # Permits broader research hypotheses with uncertainty flags


class QuestionAnalysis(BaseModel):
    """Decomposed research question intent and subtopics (Phase 10L-C)."""

    question: str = Field(...)
    core_intent: str = Field(...)
    domain: str = Field("general_science")
    subtopics: List[str] = Field(default_factory=list)
    key_entities: List[str] = Field(default_factory=list)
    search_queries: List[str] = Field(default_factory=list)
    requires_comparison: bool = Field(False)
    target_conditions: List[str] = Field(default_factory=list)


class ReferenceEntry(BaseModel):
    """Auditable citation reference entry preserving provenance (Phase 10L-C)."""

    citation_number: int = Field(...)
    citation_key: str = Field(...)  # e.g., "[1]"
    source_id: str = Field(...)
    title: str = Field(...)
    authors: List[str] = Field(default_factory=list)
    publication_year: Optional[int] = Field(None)
    doi: Optional[str] = Field(None)
    canonical_url: Optional[str] = Field(None)
    venue: Optional[str] = Field(None)
    provider: str = Field("scholarly")
    contributing_providers: List[str] = Field(default_factory=list)
    retrieval_timestamp: float = Field(default_factory=time.time)


class GroundedClaim(BaseModel):
    """Individual proposition evaluated and mapped to evidence passages (Phase 10L-C)."""

    claim_id: str = Field(default_factory=lambda: f"gclm_{uuid.uuid4().hex[:10]}")
    statement: str = Field(...)
    epistemic_status: ClaimEpistemicStatus = Field(ClaimEpistemicStatus.UNSUPPORTED)
    confidence: ConfidenceLevel = Field(ConfidenceLevel.UNVERIFIED)
    confidence_score: float = Field(0.0)
    supporting_passages: List[Dict[str, Any]] = Field(default_factory=list)
    contradicting_passages: List[Dict[str, Any]] = Field(default_factory=list)
    citation_keys: List[str] = Field(default_factory=list)  # e.g., ["[1]"]
    is_hedged: bool = Field(False)
    hedging_rationale: Optional[str] = Field(None)
    independent_sources_count: int = Field(0)


class ContradictionReport(BaseModel):
    """Detailed report of conflicting evidence across research sources (Phase 10L-C)."""

    contradiction_id: str = Field(default_factory=lambda: f"contra_{uuid.uuid4().hex[:8]}")
    topic_or_claim: str = Field(...)
    source_a_summary: str = Field(...)
    source_a_citation: Dict[str, Any] = Field(default_factory=dict)
    source_b_summary: str = Field(...)
    source_b_citation: Dict[str, Any] = Field(default_factory=dict)
    nature_of_conflict: str = Field("POLARITY_OPPOSING")  # POLARITY_OPPOSING, NUMERICAL_DISCREPANCY, CONDITIONAL_VARIATION
    resolution_or_synthesis: str = Field("")


class GroundedAnswerSynthesis(BaseModel):
    """Comprehensive evidence-grounded research answer synthesis (Phase 10L-C)."""

    synthesis_id: str = Field(default_factory=lambda: f"synth_{uuid.uuid4().hex[:10]}")
    research_question: str = Field(...)
    subtopics: List[str] = Field(default_factory=list)
    executive_summary: str = Field("")
    grounded_response: str = Field(...)
    verified_facts: List[GroundedClaim] = Field(default_factory=list)
    derived_inferences: List[GroundedClaim] = Field(default_factory=list)
    unsupported_claims: List[GroundedClaim] = Field(default_factory=list)
    contradictions: List[ContradictionReport] = Field(default_factory=list)
    uncertainties_and_gaps: List[str] = Field(default_factory=list)
    references: List[ReferenceEntry] = Field(default_factory=list)
    overall_confidence: ConfidenceLevel = Field(ConfidenceLevel.MEDIUM)
    overall_confidence_score: float = Field(0.0)
    model_used: str = Field("local_deterministic")
    is_local_model: bool = Field(True)
    duration_sec: float = Field(0.0)
    created_at: float = Field(default_factory=time.time)

    def to_markdown(self) -> str:
        """Renders synthesis as structured, publication-grade markdown with citations and provenance."""
        lines = [
            f"# Research Synthesis: {self.research_question}",
            "",
            f"**Overall Confidence**: {self.overall_confidence.value} ({self.overall_confidence_score * 100:.1f}%) | "
            f"**Model**: {self.model_used} ({'Local Model' if self.is_local_model else 'Remote Model'}) | "
            f"**Synthesis ID**: `{self.synthesis_id}`",
            "",
            "## Executive Summary",
            self.executive_summary if self.executive_summary else "No executive summary available.",
            "",
            "## Synthesized Findings",
            self.grounded_response,
            "",
        ]

        if self.verified_facts:
            lines.append("## Verified Factual Claims")
            for f in self.verified_facts:
                cites = " ".join(f.citation_keys) if f.citation_keys else "[Evidence]"
                lines.append(f"- **[Fact]** {f.statement} {cites} *(Confidence: {f.confidence.value})*")
            lines.append("")

        if self.derived_inferences:
            lines.append("## Derived Inferences & Hypotheses")
            for inf in self.derived_inferences:
                cites = " ".join(inf.citation_keys) if inf.citation_keys else ""
                lines.append(f"- **[Inference]** {inf.statement} {cites} *(Hedging: {inf.hedging_rationale or 'derived extrapolation'})*")
            lines.append("")

        if self.contradictions:
            lines.append("## Contradictions & Differing Findings")
            for c in self.contradictions:
                lines.append(f"### Conflict: {c.topic_or_claim} ({c.nature_of_conflict})")
                lines.append(f"- **Perspective A**: {c.source_a_summary} ({c.source_a_citation.get('title', 'Source A')})")
                lines.append(f"- **Perspective B**: {c.source_b_summary} ({c.source_b_citation.get('title', 'Source B')})")
                if c.resolution_or_synthesis:
                    lines.append(f"- **Synthesis Note**: {c.resolution_or_synthesis}")
            lines.append("")

        if self.unsupported_claims:
            lines.append("## Unsupported Claims & Unverified Assumptions")
            for u in self.unsupported_claims:
                lines.append(f"- **[Unsupported]** {u.statement} *(Status: {u.epistemic_status.value})*")
            lines.append("")

        if self.uncertainties_and_gaps:
            lines.append("## Evidence Gaps & Uncertainties")
            for g in self.uncertainties_and_gaps:
                lines.append(f"- {g}")
            lines.append("")

        if self.references:
            lines.append("## References & Provenance")
            for ref in self.references:
                authors_str = ", ".join(ref.authors) if ref.authors else "Unknown Authors"
                year_str = f"({ref.publication_year})" if ref.publication_year else "(n.d.)"
                venue_str = f" *{ref.venue}*." if ref.venue else ""
                doi_str = f" DOI: [{ref.doi}](https://doi.org/{ref.doi})" if ref.doi else ""
                url_str = f" [URL]({ref.canonical_url})" if ref.canonical_url and not ref.doi else ""
                lines.append(f"{ref.citation_key} {authors_str} {year_str}. **{ref.title}**.{venue_str}{doi_str}{url_str}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# Phase 10L-D: Intelligent Research Report Generation & Export Models
# =============================================================================

class ReportDetailLevel(str, Enum):
    """Enumerate research report detail levels (Phase 10L-D)."""

    SHORT = "short"                     # Concise summary, core findings table, conclusions
    DETAILED = "detailed"               # Standard academic/technical report
    COMPREHENSIVE = "comprehensive"     # Exhaustive report with full methodology, epistemic audit, contradictions


class ReportExportFormat(str, Enum):
    """Enumerate report export file formats (Phase 10L-D)."""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    ALL = "all"


class ReportExportResult(BaseModel):
    """Result payload tracking exported research report files and metrics (Phase 10L-D)."""

    report_id: str = Field(...)
    formats_generated: List[str] = Field(default_factory=list)
    file_paths: Dict[str, str] = Field(default_factory=dict)
    file_sizes_bytes: Dict[str, int] = Field(default_factory=dict)
    duration_sec: float = Field(0.0)
    exported_at: float = Field(default_factory=time.time)


class StructuredResearchReport(BaseModel):
    """Comprehensive structured research report model for Phase 10L-D."""

    report_id: str = Field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:10]}")
    title: str = Field(...)
    research_question: str = Field(...)
    detail_level: ReportDetailLevel = Field(ReportDetailLevel.COMPREHENSIVE)
    executive_summary: str = Field("")
    research_objectives: List[str] = Field(default_factory=list)
    subtopics: List[str] = Field(default_factory=list)
    introduction_and_background: str = Field("")
    literature_review: str = Field("")
    methodology_and_source_selection: str = Field("")
    evidence_backed_findings: str = Field("")
    verified_facts: List[GroundedClaim] = Field(default_factory=list)
    derived_inferences: List[GroundedClaim] = Field(default_factory=list)
    unsupported_claims: List[GroundedClaim] = Field(default_factory=list)
    contradictions: List[ContradictionReport] = Field(default_factory=list)
    contradiction_analysis: str = Field("")
    limitations_and_knowledge_gaps: List[str] = Field(default_factory=list)
    discussion_and_conclusion: str = Field("")
    references: List[ReferenceEntry] = Field(default_factory=list)
    overall_confidence: ConfidenceLevel = Field(ConfidenceLevel.MEDIUM)
    overall_confidence_score: float = Field(0.0)
    model_used: str = Field("qwen3:8b")
    is_local_model: bool = Field(True)
    export_files: Dict[str, str] = Field(default_factory=dict)
    generated_at: float = Field(default_factory=time.time)

    def to_markdown(self) -> str:
        """Renders comprehensive research report as publication-grade Markdown."""
        lines = [
            f"# {self.title}",
            "",
            f"**Research Inquiry**: {self.research_question}  ",
            f"**Detail Level**: {self.detail_level.value.upper()} | "
            f"**Confidence**: {self.overall_confidence.value} ({self.overall_confidence_score * 100:.1f}%) | "
            f"**Model**: {self.model_used} ({'Local Model' if self.is_local_model else 'Remote Model'}) | "
            f"**Report ID**: `{self.report_id}`",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            "",
            self.executive_summary if self.executive_summary else "No executive summary available.",
            "",
            "## 2. Research Objectives & Key Subtopics",
            "",
        ]

        if self.research_objectives:
            lines.append("### Research Objectives:")
            for obj in self.research_objectives:
                lines.append(f"- {obj}")
            lines.append("")

        if self.subtopics:
            lines.append("### Investigated Subtopics:")
            for st in self.subtopics:
                lines.append(f"- {st}")
            lines.append("")

        if self.introduction_and_background:
            lines.extend([
                "## 3. Introduction & Background",
                "",
                self.introduction_and_background,
                "",
            ])

        if self.literature_review:
            lines.extend([
                "## 4. Literature Review",
                "",
                self.literature_review,
                "",
            ])

        if self.methodology_and_source_selection:
            lines.extend([
                "## 5. Methodology & Source Provenance",
                "",
                self.methodology_and_source_selection,
                "",
            ])

        lines.extend([
            "## 6. Evidence-Backed Findings",
            "",
            self.evidence_backed_findings if self.evidence_backed_findings else "No empirical findings recorded.",
            "",
        ])

        if self.verified_facts:
            lines.append("### Verified Factual Claims (High Grounding)")
            lines.append("| Statement | Confidence | Citations | Independent Sources |")
            lines.append("| :--- | :--- | :--- | :---: |")
            for f in self.verified_facts:
                cites = " ".join(f.citation_keys) if f.citation_keys else "[N/A]"
                lines.append(f"| {f.statement} | {f.confidence.value} | {cites} | {f.independent_sources_count} |")
            lines.append("")

        if self.derived_inferences:
            lines.append("### Derived Inferences & Hypotheses")
            for inf in self.derived_inferences:
                cites = " ".join(inf.citation_keys) if inf.citation_keys else ""
                lines.append(f"- **[Inference]** {inf.statement} {cites} *(Hedging: {inf.hedging_rationale or 'extrapolated'})*")
            lines.append("")

        if self.contradictions or self.contradiction_analysis:
            lines.extend([
                "## 7. Contradiction & Disagreement Analysis",
                "",
                self.contradiction_analysis if self.contradiction_analysis else "Identified cross-source contradictions:",
                "",
            ])
            for c in self.contradictions:
                lines.append(f"### Conflict: {c.topic_or_claim} ({c.nature_of_conflict})")
                lines.append(f"- **Source A**: {c.source_a_summary} *({c.source_a_citation.get('title', 'Source A')})*")
                lines.append(f"- **Source B**: {c.source_b_summary} *({c.source_b_citation.get('title', 'Source B')})*")
                if c.resolution_or_synthesis:
                    lines.append(f"- **Synthesis Note**: {c.resolution_or_synthesis}")
                lines.append("")

        if self.unsupported_claims:
            lines.extend([
                "## 8. Unsupported Claims & Unverified Assumptions",
                "",
                "> **Note**: The following statements lacked passage evidence in the retrieved corpus and are strictly segregated from verified facts:",
                "",
            ])
            for u in self.unsupported_claims:
                lines.append(f"- **[Unsupported]** {u.statement} *(Status: {u.epistemic_status.value})*")
            lines.append("")

        if self.limitations_and_knowledge_gaps:
            lines.extend([
                "## 9. Research Limitations & Knowledge Gaps",
                "",
            ])
            for gap in self.limitations_and_knowledge_gaps:
                lines.append(f"- {gap}")
            lines.append("")

        if self.discussion_and_conclusion:
            lines.extend([
                "## 10. Discussion & Conclusion",
                "",
                self.discussion_and_conclusion,
                "",
            ])

        if self.references:
            lines.extend([
                "## 11. References & Bibliography",
                "",
            ])
            for ref in self.references:
                authors_str = ", ".join(ref.authors) if ref.authors else "Unknown Authors"
                year_str = f"({ref.publication_year})" if ref.publication_year else "(n.d.)"
                venue_str = f" *{ref.venue}*." if ref.venue else ""
                doi_str = f" DOI: [{ref.doi}](https://doi.org/{ref.doi})" if ref.doi else ""
                url_str = f" [URL]({ref.canonical_url})" if ref.canonical_url and not ref.doi else ""
                prov_str = f" [Providers: {', '.join(ref.contributing_providers)}]" if ref.contributing_providers else ""
                lines.append(f"{ref.citation_key} {authors_str} {year_str}. **{ref.title}**.{venue_str}{doi_str}{url_str}{prov_str}")
            lines.append("")

        return "\n".join(lines)


