"""Universal Knowledge, Research & Reasoning Engine package.

Exposes configuration, models, interfaces, exceptions, research planner, knowledge collector,
search engine, verification engine, reasoning engine, knowledge graph, repository analyzer,
document intelligence, citation engine, report generator, research memory, knowledge packages,
research agent, observability, and central UniversalResearchEngine.
"""

import sys
from typing import Any
from app.ai.research.utils import lazy_import

__all__ = [
    "ResearchConfiguration",
    "ResearchState",
    "ResearchMode",
    "SourceType",
    "EvidenceLevel",
    "KnowledgeType",
    "ConfidenceLevel",
    "ReportType",
    "ResearchStatus",
    "SubQuestion",
    "SearchStrategy",
    "ResearchPlan",
    "KnowledgeSource",
    "ClaimVerification",
    "KnowledgeGraphNode",
    "KnowledgeGraphEdge",
    "RepositorySummary",
    "DocumentAnalysis",
    "CitationItem",
    "ResearchReport",
    "KnowledgePackage",
    "ReasoningOutput",
    "ResearchMemoryItem",
    "ResearchMetrics",
    "ResearchHealth",
    "IResearchEngine",
    "IResearchPlanner",
    "ISearchEngine",
    "IKnowledgeCollector",
    "IVerificationEngine",
    "IReasoningEngine",
    "IKnowledgeGraph",
    "IRepositoryAnalyzer",
    "IDocumentIntelligence",
    "ICitationEngine",
    "IReportGenerator",
    "IResearchMemory",
    "IResearchAgent",
    "IResearchManager",
    "ResearchEngineError",
    "ResearchPlanner",
    "KnowledgeCollector",
    "SearchEngine",
    "VerificationEngine",
    "ReasoningEngine",
    "KnowledgeGraph",
    "RepositoryAnalyzer",
    "DocumentIntelligence",
    "CitationEngine",
    "ReportGenerator",
    "ResearchMemory",
    "KnowledgePackageManager",
    "ResearchAgent",
    "ResearchMetricsTracker",
    "ResearchHealthMonitor",
    "ResearchCache",
    "MockResearchProvider",
    "ResearchManager",
    "UniversalResearchEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
