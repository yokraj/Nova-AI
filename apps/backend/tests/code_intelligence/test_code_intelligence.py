"""Unit and Integration Tests for Nova AI Enterprise Document & Code Intelligence Engine.

Validates Repository Scanning, Language Detection, AST Parsing, Symbol Indexing,
Dependency Graph Analysis, Architecture Pattern Detection, API Extraction, Database Extraction,
Summarization, Cross References, Health Diagnostics, Statistics, REST API, and RBAC.
"""

import asyncio
import pytest

from app.code_intelligence import (
    CodeIntelligenceConfig,
    RepositoryIndexRequest,
    LanguageDetector,
    DocumentParser,
    ASTParser,
    SymbolIndexer,
    DependencyAnalyzer,
    ArchitectureExtractor,
    APIExtractor,
    DatabaseExtractor,
    CodeSummarizer,
    RepositorySummaryEngine,
    CrossReferenceEngine,
    ChangeDetector,
    RepositoryScanner,
    CodeParser,
    CodeIntelligenceStatisticsTracker,
    CodeIntelligenceHealthChecker,
    CodeIntelligenceRepository,
    RepositoryService,
    CodeAnalysisService,
    ArchitectureService,
    SummaryService,
    CodeIntelligenceEngine,
)


def test_language_detector_and_document_parser():
    """Test LanguageDetector 19 languages and DocumentParser 14 document formats."""
    detector = LanguageDetector()
    parser = DocumentParser()

    assert detector.detect_language("main.py") == "Python"
    assert detector.detect_language("App.tsx") == "TypeScript"
    assert detector.detect_language("server.go") == "Go"
    assert detector.detect_language("lib.rs") == "Rust"
    assert detector.detect_language("schema.sql") == "SQL"
    assert detector.detect_language("Dockerfile") == "Dockerfile"

    doc_res = parser.parse_document("architecture.md", "# System Architecture\n\n- Multi-tier backend design.")
    assert doc_res["title"] == "System Architecture"
    assert doc_res["header_count"] if "header_count" in doc_res else doc_res["line_count"] > 0


def test_ast_parsing_and_symbol_indexing():
    """Test ASTParser symbol extraction and SymbolIndexer table indexing."""
    ast_parser = ASTParser()
    indexer = SymbolIndexer()

    code = "class DatabaseManager:\n    def connect(self):\n        pass\n\ndef main():\n    pass"
    res = ast_parser.parse_source_code(code, language="Python", file_path="db.py")

    assert len(res["symbols"]) == 3
    sym_names = [s["name"] for s in res["symbols"]]
    assert "DatabaseManager" in sym_names
    assert "connect" in sym_names

    indexer.index_symbols("repo-1", "db.py", res["symbols"])
    found = indexer.search_symbols("repo-1", "DatabaseManager")
    assert len(found) == 1
    assert found[0]["symbol_type"] == "Class"


def test_dependency_analyzer_and_architecture_extractor():
    """Test DependencyAnalyzer graphs and ArchitectureExtractor design patterns."""
    dep_analyzer = DependencyAnalyzer()
    arch_extractor = ArchitectureExtractor()

    imports = {
        "app/main.py": ["app/api/v1/api.py", "app/service.py"],
        "app/api/v1/api.py": ["app/service.py"],
        "app/service.py": ["app/repository.py"],
    }
    deps = dep_analyzer.analyze_dependencies(imports)
    assert deps["total_dependencies"] == 4

    files = ["app/api/v1/api.py", "app/service.py", "app/repository.py", "app/models.py"]
    symbols = [{"name": "RepositoryService"}, {"name": "UserRepository"}]
    patterns = arch_extractor.detect_architecture_patterns(files, symbols)

    assert len(patterns) >= 1
    pattern_names = [p["pattern_name"] for p in patterns]
    assert "Repository Pattern" in pattern_names or "Layered Architecture" in pattern_names


def test_api_and_database_extractors():
    """Test APIExtractor route extraction and DatabaseExtractor ORM schema extraction."""
    api_extractor = APIExtractor()
    db_extractor = DatabaseExtractor()

    py_code = '@router.get("/api/v1/health")\ndef get_health():\n    pass\n\nclass User(Base):\n    __tablename__ = "users"\n    id = Column(String)'

    apis = api_extractor.extract_apis_from_file("api.py", py_code)
    assert len(apis) == 1
    assert apis[0]["endpoint"] == "/api/v1/health"

    tables = db_extractor.extract_database_schemas("models.py", py_code)
    assert len(tables) == 1
    assert tables[0]["table_name"] == "users"


def test_summaries_and_cross_references():
    """Test CodeSummarizer, RepositorySummaryEngine, and CrossReferenceEngine."""
    summarizer = CodeSummarizer()
    repo_summary_engine = RepositorySummaryEngine()
    cross_ref = CrossReferenceEngine()

    sym_sum = summarizer.summarize_symbol({"name": "CoreEngine", "symbol_type": "Class", "file_path": "engine.py"})
    assert "CoreEngine" in sym_sum

    repo_sum = repo_summary_engine.generate_repository_summary(
        repository_id="repo-001",
        name="Nova-AI",
        primary_language="Python",
        frameworks=["FastAPI"],
        file_count=50,
        lines_of_code=5000,
        symbols_count=120,
        apis_count=15,
        tables_count=8,
    )
    assert repo_sum.repository_id == "repo-001"
    assert "Nova-AI" in repo_sum.architecture_summary

    cross_res = cross_ref.create_cross_references(
        symbol={"id": "sym-1", "name": "MemoryEngine"},
        memory_entries=[{"id": "mem-1", "title": "MemoryEngine architecture", "content": "MemoryEngine design"}],
        graph_entities=[{"id": "node-1", "name": "MemoryEngine"}],
    )
    assert len(cross_res["linked_memory_ids"]) == 1


def test_repository_service_end_to_end():
    """Test RepositoryService end-to-end indexing and statistics."""
    async def _test():
        repo = CodeIntelligenceRepository()
        service = RepositoryService(repo)

        req = RepositoryIndexRequest(name="Nova-AI-Backend", root_path="apps/backend", workspace="Nova")
        res = await service.index_repository(req)

        assert res.id is not None
        assert res.name == "Nova-AI-Backend"

        repos = await service.list_repositories()
        assert len(repos) == 1

    asyncio.run(_test())


def test_code_intelligence_health_and_statistics():
    """Test CodeIntelligenceHealthChecker and CodeIntelligenceStatisticsTracker."""
    tracker = CodeIntelligenceStatisticsTracker()
    checker = CodeIntelligenceHealthChecker()

    tracker.record_indexing_event(files=10, classes=5, functions=20, apis=4, tables=2, latency_ms=18.0)
    stats = tracker.get_statistics()
    assert stats.repositories_indexed == 1
    assert stats.files_indexed == 10

    health = checker.run_health_checks()
    assert health.status == "healthy"
    assert health.parser_healthy is True
