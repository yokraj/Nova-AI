"""Central Universal Research Engine facade unifying knowledge collection, verification, reasoning, and reports.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.research.cache import ResearchCache
from app.ai.research.citation_engine import CitationEngine
from app.ai.research.configuration import ResearchConfiguration
from app.ai.research.document_intelligence import DocumentIntelligence
from app.ai.research.health import ResearchHealthMonitor
from app.ai.research.interfaces import IResearchEngine
from app.ai.research.knowledge_collector import KnowledgeCollector
from app.ai.research.knowledge_graph import KnowledgeGraph
from app.ai.research.knowledge_packages import KnowledgePackageManager
from app.ai.research.metrics import ResearchMetricsTracker
from app.ai.research.models import (
    CitationItem,
    DocumentAnalysis,
    KnowledgePackage,
    KnowledgeSource,
    RepositorySummary,
    ResearchHealth,
    ResearchMemoryItem,
    ResearchMetrics,
    ResearchReport,
    ResearchState,
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
