"""Nova AI Enterprise Document & Code Intelligence Engine Package.

Exports language detectors, document parsers, AST parsers, symbol indexers, dependency analyzers,
architecture extractors, API extractors, database extractors, documentation extractors, code summarizers,
cross-reference engines, change detectors, incremental indexers, metadata extractors, repository scanners,
statistics trackers, health checkers, services, and CodeIntelligenceEngine master orchestrator.
"""

from app.code_intelligence.config import CodeIntelligenceConfig
from app.code_intelligence.exceptions import (
    CodeIntelligenceError,
    RepositoryScanError,
    LanguageNotSupportedError,
    ASTParseError,
    SymbolIndexingError,
    ArchitectureExtractionError,
    APIExtractionError,
    DatabaseExtractionError,
    CodeIntelligenceHealthError,
)
from app.code_intelligence.models import (
    RepositoryModel,
    CodeSymbolModel,
    CodeDependencyModel,
    ArchitectureComponentModel,
    CodeStatisticsModel,
)
from app.code_intelligence.schemas import (
    RepositoryIndexRequest,
    RepositoryResponse,
    CodeSymbolResponse,
    ArchitecturePatternResponse,
    APISchemaResponse,
    DatabaseSchemaResponse,
    RepositorySummaryResponse,
    CodeHealthResponse,
    CodeStatisticsResponse,
)
from app.code_intelligence.language_detector import LanguageDetector
from app.code_intelligence.document_parser import DocumentParser
from app.code_intelligence.ast_parser import ASTParser
from app.code_intelligence.symbol_indexer import SymbolIndexer
from app.code_intelligence.dependency_analyzer import DependencyAnalyzer
from app.code_intelligence.architecture_extractor import ArchitectureExtractor
from app.code_intelligence.api_extractor import APIExtractor
from app.code_intelligence.database_extractor import DatabaseExtractor
from app.code_intelligence.documentation_extractor import DocumentationExtractor
from app.code_intelligence.code_summarizer import CodeSummarizer
from app.code_intelligence.repository_summary import RepositorySummaryEngine
from app.code_intelligence.cross_reference import CrossReferenceEngine
from app.code_intelligence.change_detector import ChangeDetector
from app.code_intelligence.incremental_indexer import IncrementalIndexer
from app.code_intelligence.metadata import CodeMetadataExtractor
from app.code_intelligence.repository_scanner import RepositoryScanner
from app.code_intelligence.code_parser import CodeParser
from app.code_intelligence.statistics import CodeIntelligenceStatisticsTracker
from app.code_intelligence.health import CodeIntelligenceHealthChecker
from app.code_intelligence.repository import CodeIntelligenceRepository
from app.code_intelligence.service import (
    RepositoryService,
    DocumentService,
    CodeAnalysisService,
    DependencyService,
    ArchitectureService,
    SummaryService,
)
from app.code_intelligence.engine import CodeIntelligenceEngine

__all__ = [
    "CodeIntelligenceConfig",
    "CodeIntelligenceError",
    "RepositoryScanError",
    "LanguageNotSupportedError",
    "ASTParseError",
    "SymbolIndexingError",
    "ArchitectureExtractionError",
    "APIExtractionError",
    "DatabaseExtractionError",
    "CodeIntelligenceHealthError",
    "RepositoryModel",
    "CodeSymbolModel",
    "CodeDependencyModel",
    "ArchitectureComponentModel",
    "CodeStatisticsModel",
    "RepositoryIndexRequest",
    "RepositoryResponse",
    "CodeSymbolResponse",
    "ArchitecturePatternResponse",
    "APISchemaResponse",
    "DatabaseSchemaResponse",
    "RepositorySummaryResponse",
    "CodeHealthResponse",
    "CodeStatisticsResponse",
    "LanguageDetector",
    "DocumentParser",
    "ASTParser",
    "SymbolIndexer",
    "DependencyAnalyzer",
    "ArchitectureExtractor",
    "APIExtractor",
    "DatabaseExtractor",
    "DocumentationExtractor",
    "CodeSummarizer",
    "RepositorySummaryEngine",
    "CrossReferenceEngine",
    "ChangeDetector",
    "IncrementalIndexer",
    "CodeMetadataExtractor",
    "RepositoryScanner",
    "CodeParser",
    "CodeIntelligenceStatisticsTracker",
    "CodeIntelligenceHealthChecker",
    "CodeIntelligenceRepository",
    "RepositoryService",
    "DocumentService",
    "CodeAnalysisService",
    "DependencyService",
    "ArchitectureService",
    "SummaryService",
    "CodeIntelligenceEngine",
]
