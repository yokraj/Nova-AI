"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.research.
"""

import importlib
from typing import Any, Dict, List

_LAZY_MAP: Dict[str, str] = {
    "ResearchConfiguration": "app.ai.research.configuration",
    "ResearchState": "app.ai.research.models",
    "ResearchMode": "app.ai.research.models",
    "SourceType": "app.ai.research.models",
    "EvidenceLevel": "app.ai.research.models",
    "KnowledgeType": "app.ai.research.models",
    "ConfidenceLevel": "app.ai.research.models",
    "ReportType": "app.ai.research.models",
    "ResearchStatus": "app.ai.research.models",
    "SubQuestion": "app.ai.research.models",
    "SearchStrategy": "app.ai.research.models",
    "ResearchPlan": "app.ai.research.models",
    "KnowledgeSource": "app.ai.research.models",
    "ClaimVerification": "app.ai.research.models",
    "KnowledgeGraphNode": "app.ai.research.models",
    "KnowledgeGraphEdge": "app.ai.research.models",
    "RepositorySummary": "app.ai.research.models",
    "DocumentAnalysis": "app.ai.research.models",
    "CitationItem": "app.ai.research.models",
    "ResearchReport": "app.ai.research.models",
    "KnowledgePackage": "app.ai.research.models",
    "ReasoningOutput": "app.ai.research.models",
    "ResearchMemoryItem": "app.ai.research.models",
    "ResearchMetrics": "app.ai.research.models",
    "ResearchHealth": "app.ai.research.models",
    "IResearchEngine": "app.ai.research.interfaces",
    "IResearchPlanner": "app.ai.research.interfaces",
    "ISearchEngine": "app.ai.research.interfaces",
    "IKnowledgeCollector": "app.ai.research.interfaces",
    "IVerificationEngine": "app.ai.research.interfaces",
    "IReasoningEngine": "app.ai.research.interfaces",
    "IKnowledgeGraph": "app.ai.research.interfaces",
    "IRepositoryAnalyzer": "app.ai.research.interfaces",
    "IDocumentIntelligence": "app.ai.research.interfaces",
    "ICitationEngine": "app.ai.research.interfaces",
    "IReportGenerator": "app.ai.research.interfaces",
    "IResearchMemory": "app.ai.research.interfaces",
    "IResearchAgent": "app.ai.research.interfaces",
    "IResearchManager": "app.ai.research.interfaces",
    "ResearchEngineError": "app.ai.research.exceptions",
    "ResearchPlanner": "app.ai.research.research_planner",
    "KnowledgeCollector": "app.ai.research.knowledge_collector",
    "SearchEngine": "app.ai.research.search_engine",
    "VerificationEngine": "app.ai.research.verification_engine",
    "ReasoningEngine": "app.ai.research.reasoning_engine",
    "KnowledgeGraph": "app.ai.research.knowledge_graph",
    "RepositoryAnalyzer": "app.ai.research.repository_analyzer",
    "DocumentIntelligence": "app.ai.research.document_intelligence",
    "CitationEngine": "app.ai.research.citation_engine",
    "ReportGenerator": "app.ai.research.report_generator",
    "ResearchMemory": "app.ai.research.research_memory",
    "KnowledgePackageManager": "app.ai.research.knowledge_packages",
    "ResearchAgent": "app.ai.research.research_agent",
    "ResearchMetricsTracker": "app.ai.research.metrics",
    "ResearchHealthMonitor": "app.ai.research.health",
    "ResearchCache": "app.ai.research.cache",
    "MockResearchProvider": "app.ai.research.mock_provider",
    "ResearchManager": "app.ai.research.research_manager",
    "UniversalResearchEngine": "app.ai.research.research_engine",
    "EvidenceGraphBuilder": "app.ai.research.evidence_graph_builder",
    "ClaimVerificationOutcome": "app.ai.research.models",
    "ClaimType": "app.ai.research.models",
    "SourcePassage": "app.ai.research.models",
    "AtomicClaim": "app.ai.research.models",
    "EvidenceRelation": "app.ai.research.models",
    "ClaimVerificationDetail": "app.ai.research.models",
    "ClaimEpistemicStatus": "app.ai.research.models",
    "SynthesisMode": "app.ai.research.models",
    "QuestionAnalysis": "app.ai.research.models",
    "ReferenceEntry": "app.ai.research.models",
    "GroundedClaim": "app.ai.research.models",
    "ContradictionReport": "app.ai.research.models",
    "GroundedAnswerSynthesis": "app.ai.research.models",
    "ResearchQuestionAnalyzer": "app.ai.research.question_analyzer",
    "ResearchContradictionDetector": "app.ai.research.contradiction_detector",
    "ClaimCitationMapper": "app.ai.research.citation_mapper",
    "EpistemicClassifier": "app.ai.research.epistemic_classifier",
    "EvidenceGroundedSynthesizer": "app.ai.research.answer_synthesizer",
    "ReportDetailLevel": "app.ai.research.models",
    "ReportExportFormat": "app.ai.research.models",
    "ReportExportResult": "app.ai.research.models",
    "StructuredResearchReport": "app.ai.research.models",
    "NativePDFWriter": "app.ai.research.pdf_writer",
    "ResearchReportExporter": "app.ai.research.report_exporter",
    "IntelligentReportGenerator": "app.ai.research.intelligent_report_generator",
}


def lazy_import(name: str) -> Any:
    """Lazy imports a symbol based on the module map.

    Args:
        name: Name of symbol to import.

    Returns:
        The imported symbol object.
    """
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module 'app.ai.research' has no attribute '{name}'")


def format_markdown_report(title: str, summary: str, details: str) -> str:
    """Formats markdown report string.

    Args:
        title: Topic header.
        summary: Executive summary text.
        details: Technical details text.

    Returns:
        Formatted markdown string.
    """
    return f"# {title}\n\n## Executive Summary\n{summary}\n\n## Technical Findings\n{details}"
