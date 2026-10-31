"""Central Universal Research Engine facade unifying knowledge collection, verification, reasoning, and reports.
"""

from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union
from app.ai.research.cache import ResearchCache
from app.ai.research.citation_engine import CitationEngine
from app.ai.research.configuration import ResearchConfiguration
from app.ai.research.document_intelligence import DocumentIntelligence
from app.ai.research.health import ResearchHealthMonitor
from app.ai.research.interfaces import IResearchEngine
from app.ai.research.evidence_graph_builder import EvidenceGraphBuilder
from app.ai.research.answer_synthesizer import EvidenceGroundedSynthesizer
from app.ai.research.intelligent_report_generator import IntelligentReportGenerator
from app.ai.research.report_exporter import ResearchReportExporter
from app.ai.research.knowledge_collector import KnowledgeCollector
from app.ai.research.knowledge_graph import KnowledgeGraph
from app.ai.research.knowledge_packages import KnowledgePackageManager
from app.ai.research.metrics import ResearchMetricsTracker
from app.ai.research.models import (
    CitationItem,
    DocumentAnalysis,
    GroundedAnswerSynthesis,
    KnowledgePackage,
    KnowledgeSource,
    ReportDetailLevel,
    ReportExportFormat,
    ReportExportResult,
    RepositorySummary,
    ResearchHealth,
    ResearchMemoryItem,
    ResearchMetrics,
    ResearchReport,
    ResearchState,
    StructuredResearchReport,
    SynthesisMode,
)
from app.ai.research.reasoning_engine import ReasoningEngine
from app.ai.research.report_generator import ReportGenerator
from app.ai.research.repository_analyzer import RepositoryAnalyzer
from app.ai.research.research_agent import ResearchAgent
from app.ai.research.research_manager import ResearchManager
from app.ai.research.research_memory import ResearchMemory
from app.ai.research.research_planner import ResearchPlanner
from app.ai.research.search_engine import SearchEngine
from app.ai.research.verification_engine import VerificationEngine


class UniversalResearchEngine(IResearchEngine):
    """The central Universal Knowledge, Research & Reasoning Engine runtime for Nova AI."""

    def __init__(self, config: Optional[ResearchConfiguration] = None) -> None:
        self.config = config or ResearchConfiguration()
        self.manager = ResearchManager(self.config)
        self.planner = ResearchPlanner()
        self.collector = KnowledgeCollector()
        self.search_engine_sub = SearchEngine(self.collector)
        self.verifier = VerificationEngine()
        self.reasoner = ReasoningEngine()
        self.graph = KnowledgeGraph()
        self.repo_analyzer = RepositoryAnalyzer()
        self.doc_intelligence = DocumentIntelligence()
        self.citation_engine = CitationEngine()
        self.report_generator = ReportGenerator()
        self.memory = ResearchMemory()
        self.pkg_manager = KnowledgePackageManager()
        self.agent = ResearchAgent()
        self.metrics_tracker = ResearchMetricsTracker()
        self.health_monitor = ResearchHealthMonitor()
        self.cache = ResearchCache(ttl_seconds=self.config.cache_ttl_seconds)
        self.evidence_builder = EvidenceGraphBuilder(graph=self.graph)
        self.synthesizer = EvidenceGroundedSynthesizer(lit_discovery=self.search_engine_sub.lit_discovery)
        self.report_exporter = ResearchReportExporter()
        self.intelligent_report_generator = IntelligentReportGenerator(
            synthesizer=self.synthesizer,
            exporter=self.report_exporter,
        )

        self._active_citations: List[CitationItem] = []

    async def research(self, topic: str, **kwargs: Any) -> ResearchReport:
        """Performs end-to-end autonomous research synthesis.

        Args:
            topic: Research inquiry string.
            **kwargs: Extra parameters (mode, filters, style).

        Returns:
            Synthesized ResearchReport payload.
        """
        start_time = time.time()
        cached = self.cache.get(f"research_{topic}")
        if cached:
            return cached

        # 1. Create Research Plan
        plan = await self.planner.create_plan(topic, **kwargs)

        # 2. Search & Collect Sources
        sources = await self.search_engine_sub.search(topic)

        # 3. Cross-Verify Claims
        verified_claims = []
        for sq in plan.sub_questions:
            clm = await self.verifier.verify_claim(sq.query, sources)
            verified_claims.append(clm)

        # 4. Reason & Derive Conclusions
        reasoning_out = await self.reasoner.reason(topic, verified_claims)

        # 5. Format Citations & Generate Report
        citations_list = [self.citation_engine.generate_citation(src, style=self.config.default_citation_style) for src in sources]
        self._active_citations = citations_list

        report = await self.report_generator.generate_report(topic, reasoning_out, citations_list)

        # 6. Save Session Memory
        mem_item = ResearchMemoryItem(topic=topic, plan=plan, report=report, citations_count=len(citations_list))
        await self.memory.save_session(mem_item)

        elapsed = time.time() - start_time
        self.metrics_tracker.record_research(len(sources), len(verified_claims), elapsed)
        self.cache.set(f"research_{topic}", report)

        return report

    async def search(self, query: str, **kwargs: Any) -> List[KnowledgeSource]:
        """Searches local and external knowledge sources."""
        return await self.search_engine_sub.search(query, **kwargs)

    async def discover_literature(
        self,
        query: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        year: Optional[int] = None,
        doi: Optional[str] = None,
        limit: int = 10,
        selected_providers: Optional[List[str]] = None,
    ):
        """Executes Phase 10L-A literature discovery across Crossref, OpenAlex, arXiv, and Europe PMC."""
        return self.search_engine_sub.lit_discovery.search_literature(
            query=query,
            title=title,
            author=author,
            year=year,
            doi=doi,
            limit=limit,
            selected_providers=selected_providers,
        )

    async def verify_doi(self, doi: str, expected_record: Any = None):
        """Executes Phase 10L-A DOI validation and registry metadata comparison."""
        return self.search_engine_sub.lit_discovery.verify_doi(doi=doi, expected_record=expected_record)

    async def analyze_document(self, doc_path: str) -> DocumentAnalysis:
        """Parses document into structured knowledge model."""
        return await self.doc_intelligence.analyze_document(doc_path)

    async def analyze_repository(self, repo_path: str) -> RepositorySummary:
        """Analyzes codebase structure and architecture."""
        return await self.repo_analyzer.analyze_repository(repo_path)

    async def generate_report(self, topic: str, **kwargs: Any) -> ResearchReport:
        """Generates research report."""
        return await self.research(topic, **kwargs)

    async def knowledge_graph(self) -> Dict[str, Any]:
        """Returns local Knowledge Graph node and edge counts."""
        return self.graph.export_graph_summary()

    def build_evidence_graph(
        self,
        records: Optional[List[Any]] = None,
    ) -> EvidenceGraphBuilder:
        """Constructs or updates the evidence and provenance graph from scholarly sources (Phase 10L-B)."""
        if records:
            self.evidence_builder.build_from_scholarly_records(records)
        return self.evidence_builder

    def get_evidence_graph(self) -> EvidenceGraphBuilder:
        """Returns the active EvidenceGraphBuilder instance (Phase 10L-B)."""
        return self.evidence_builder

    async def synthesize_answer(
        self,
        question: str,
        sources: Optional[List[Any]] = None,
        mode: SynthesisMode = SynthesisMode.GROUNDED_STRICT,
        candidate_claims: Optional[List[str]] = None,
        max_sources: int = 8,
        model_id: str = "qwen3:8b",
        **kwargs: Any,
    ) -> GroundedAnswerSynthesis:
        """Executes Phase 10L-C Evidence-Grounded Research Answer Synthesis.

        Args:
            question: Complex research inquiry or question.
            sources: Pre-retrieved source records or None.
            mode: SynthesisMode (GROUNDED_STRICT, BALANCED, EXPLORATORY).
            candidate_claims: Optional list of specific claims to evaluate.
            max_sources: Maximum scholarly sources to retrieve/ingest.
            model_id: Local Ollama model ID (default 'qwen3:8b').

        Returns:
            GroundedAnswerSynthesis payload with claim-level citations and provenance.
        """
        return await self.synthesizer.synthesize(
            question=question,
            sources=sources,
            evidence_builder=self.evidence_builder,
            mode=mode,
            candidate_claims=candidate_claims,
            max_sources=max_sources,
            model_id=model_id,
        )

    async def generate_research_report(
        self,
        question_or_synthesis: Union[str, GroundedAnswerSynthesis],
        sources: Optional[List[Any]] = None,
        detail_level: ReportDetailLevel = ReportDetailLevel.COMPREHENSIVE,
        candidate_claims: Optional[List[str]] = None,
        title: Optional[str] = None,
        model_id: str = "qwen3:8b",
        export_formats: Optional[List[ReportExportFormat]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        base_filename: Optional[str] = None,
        **kwargs: Any,
    ) -> StructuredResearchReport:
        """Executes Phase 10L-D Intelligent Research Report Generation & Export.

        Args:
            question_or_synthesis: Raw inquiry string or pre-computed GroundedAnswerSynthesis.
            sources: Optional scholarly source records.
            detail_level: ReportDetailLevel (SHORT, DETAILED, COMPREHENSIVE).
            candidate_claims: Optional explicit claims to evaluate.
            title: Custom title for report.
            model_id: Local Ollama model ID (default 'qwen3:8b').
            export_formats: List of formats to export (MARKDOWN, HTML, PDF, ALL).
            output_dir: Directory to save exported files.
            base_filename: Base filename prefix for export files.

        Returns:
            StructuredResearchReport model containing all sections and export paths.
        """
        if isinstance(question_or_synthesis, GroundedAnswerSynthesis):
            report = await self.intelligent_report_generator.generate_from_synthesis(
                synthesis=question_or_synthesis,
                detail_level=detail_level,
                title=title,
                model_id=model_id,
            )
            if export_formats and output_dir:
                out_p = Path(output_dir)
                out_p.mkdir(parents=True, exist_ok=True)
                fname = base_filename or f"report_{report.report_id}"
                if ReportExportFormat.ALL in export_formats or (
                    ReportExportFormat.MARKDOWN in export_formats
                    and ReportExportFormat.HTML in export_formats
                    and ReportExportFormat.PDF in export_formats
                ):
                    self.report_exporter.export_all(report, out_p, fname)
                else:
                    if ReportExportFormat.MARKDOWN in export_formats:
                        md_path = out_p / f"{fname}.md"
                        self.report_exporter.export_markdown(report, md_path)
                        report.export_files["markdown"] = str(md_path)
                    if ReportExportFormat.HTML in export_formats:
                        html_path = out_p / f"{fname}.html"
                        self.report_exporter.export_html(report, html_path)
                        report.export_files["html"] = str(html_path)
                    if ReportExportFormat.PDF in export_formats:
                        pdf_path = out_p / f"{fname}.pdf"
                        self.report_exporter.export_pdf(report, pdf_path)
                        report.export_files["pdf"] = str(pdf_path)
            return report
        else:
            return await self.intelligent_report_generator.generate_report(
                question=question_or_synthesis,
                sources=sources,
                detail_level=detail_level,
                candidate_claims=candidate_claims,
                title=title,
                model_id=model_id,
                export_formats=export_formats,
                output_dir=output_dir,
                base_filename=base_filename,
            )

    async def citations(self) -> List[CitationItem]:
        """Retrieves active citations list."""
        return self._active_citations

    async def research_history(self) -> List[ResearchMemoryItem]:
        """Retrieves research session history."""
        return await self.memory.list_history()

    async def continue_research(self, topic: str, new_query: str) -> ResearchReport:
        """Resumes previous research session for incremental research inquiry."""
        prior = await self.memory.get_session(topic)
        combined_query = f"{topic} {new_query}" if prior else new_query
        return await self.research(combined_query)

    async def knowledge_package(self, topic: str) -> KnowledgePackage:
        """Retrieves or creates reusable Knowledge Package."""
        pkg = self.pkg_manager.get_package(topic)
        if not pkg:
            pkg = KnowledgePackage(
                topic=topic,
                documentation=f"Stored documentation knowledge package for {topic}.",
                examples=[f"// Example implementation for {topic}"],
                best_practices=[f"Use modular patterns for {topic}"],
                common_errors=[f"Invalid configuration for {topic}"],
            )
            self.pkg_manager.save_package(pkg)
        return pkg

    async def check_health(self) -> ResearchHealth:
        """Retrieves research health diagnostics."""
        summary = self.graph.export_graph_summary()
        return self.health_monitor.check_health(ResearchState.COMPLETED, summary["nodes_count"], summary["edges_count"])

    async def get_metrics(self) -> ResearchMetrics:
        """Retrieves research telemetry metrics."""
        return self.metrics_tracker.get_metrics()
