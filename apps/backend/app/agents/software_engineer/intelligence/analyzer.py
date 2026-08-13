"""Main CodeIntelligenceAnalyzer coordinating workspace AST semantic analysis.
"""

import hashlib
import os
import time
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.intelligence.ast_parser import PythonASTParser
from app.agents.software_engineer.intelligence.cache import CachePayload, FileSystemCacheProvider
from app.agents.software_engineer.intelligence.call_graph import build_call_graph
from app.agents.software_engineer.intelligence.complexity import ASTComplexityAnalyzer
from app.agents.software_engineer.intelligence.dead_code import ASTDeadCodeAnalyzer
from app.agents.software_engineer.intelligence.dependency_graph import ModuleDependencyAnalyzer
from app.agents.software_engineer.intelligence.duplicate_detector import ASTDuplicateDetector
from app.agents.software_engineer.intelligence.exceptions import (
    CodeIntelligenceError,
)
from app.agents.software_engineer.repository.exceptions import (
    InvalidRepositoryError,
    RepositoryNotFoundError,
)
from app.agents.software_engineer.intelligence.interfaces import IntelligenceAnalyzer
from app.agents.software_engineer.intelligence.models import (
    AnalysisMetadata,
    AnalysisResult,
    ClassInfo,
    ComplexityReport,
    DeadCodeReport,
    DependencyGraph,
    DuplicateReport,
    FunctionInfo,
    ImportInfo,
    IntelligenceReport,
    RepositoryIntelligenceSummary,
    Symbol,
)
from app.agents.software_engineer.intelligence.reference_finder import ReferenceFinder
from app.agents.software_engineer.intelligence.symbol_index import InMemorySymbolIndex
from app.agents.software_engineer.intelligence.utils import load_file_safely


class CodeIntelligenceAnalyzer(IntelligenceAnalyzer):
    """Orchestrates multi-stage workspace analysis compiling AST intelligence reports."""

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = workspace_root
        self.parser = PythonASTParser()
        self.indexer = InMemorySymbolIndex()
        self.dep_analyzer = ModuleDependencyAnalyzer()
        self.complexity_analyzer = ASTComplexityAnalyzer()
        self.dup_detector = ASTDuplicateDetector()
        self.dead_analyzer = ASTDeadCodeAnalyzer()
        self.ref_finder = ReferenceFinder()
        self.cache: Optional[FileSystemCacheProvider] = None

    def _get_cache_path(self, workspace_path: str) -> str:
        return os.path.join(workspace_path, ".nova", "intelligence_cache.json")

    def validate_workspace(self, workspace_path: str) -> None:
        """Validates workspace directory.

        Raises:
            RepositoryNotFoundError: If workspace path does not exist.
            InvalidRepositoryError: If workspace path is not readable.
        """
        if not workspace_path:
            raise InvalidRepositoryError("Workspace path cannot be empty.")

        abs_path = os.path.abspath(workspace_path)
        if not os.path.exists(abs_path):
            raise RepositoryNotFoundError(f"Workspace path does not exist: {abs_path}")

        if not os.path.isdir(abs_path):
            raise InvalidRepositoryError(f"Workspace path is not a directory: {abs_path}")

        if not os.access(abs_path, os.R_OK):
            raise InvalidRepositoryError(f"Workspace path is not readable: {abs_path}")

    def analyze_repository(self, workspace_path: str) -> IntelligenceReport:
        """Executes deep source code analysis of the workspace.

        Args:
            workspace_path: Workspace directory.

        Returns:
            Complete IntelligenceReport payload details.
        """
        start_time = time.perf_counter()
        self.validate_workspace(workspace_path)
        abs_workspace = os.path.abspath(workspace_path)

        # 1. Setup Caching
        cache_file = self._get_cache_path(abs_workspace)
        self.cache = FileSystemCacheProvider(cache_file)

        # 2. Collect all Python source files
        python_files: List[str] = []
        for root, dirs, files in os.walk(abs_workspace):
            # Prune default ignored dirs early to optimize performance
            dirs[:] = [
                d
                for d in dirs
                if d
                not in (
                    ".git",
                    ".venv",
                    "venv",
                    "node_modules",
                    "__pycache__",
                    "dist",
                    "build",
                    ".pytest_cache",
                )
            ]
            for f in files:
                if f.endswith(".py"):
                    abs_fp = os.path.join(root, f)
                    rel_fp = os.path.relpath(abs_fp, abs_workspace)
                    python_files.append(rel_fp)

        # 3. Analyze each file (incremental check)
        ast_trees: Dict[str, Any] = {}
        all_symbols: Dict[str, Symbol] = {}
        all_classes: List[ClassInfo] = []
        all_functions: List[FunctionInfo] = []
        file_imports: Dict[str, List[ImportInfo]] = {}
        complexity_reports: Dict[str, ComplexityReport] = {}
        cache_used = False

        for rel_fp in python_files:
            abs_fp = os.path.join(abs_workspace, rel_fp)
            stat = os.stat(abs_fp)
            size = stat.st_size
            mtime = stat.st_mtime

            # Compute simple content SHA256
            source_content = load_file_safely(abs_fp)
            content_hash = hashlib.sha256(source_content.encode("utf-8")).hexdigest()

            # Cache lookup
            cached_data = self.cache.get(rel_fp)
            if (
                cached_data
                and cached_data["mtime"] == mtime
                and cached_data["size"] == size
                and cached_data["hash"] == content_hash
            ):
                # Cache hit! Parse stored symbols
                payload = CachePayload.model_validate(cached_data)

                # Reconstruct models from cache dicts
                symbols = [Symbol.model_validate(s) for s in payload.symbols]
                classes = [ClassInfo.model_validate(c) for c in payload.classes]
                functions = [FunctionInfo.model_validate(f) for f in payload.functions]
                imports = [ImportInfo.model_validate(i) for i in payload.imports]
                complexity = ComplexityReport.model_validate(payload.complexity)

                # Reconstruct raw AST in memory for dependencies/graphing
                try:
                    ast_trees[rel_fp] = ast.parse(source_content, filename=abs_fp)
                except Exception:
                    ast_trees[rel_fp] = None

                cache_used = True
            else:
                # Cache miss! Complete AST parse
                try:
                    parsed = self.parser.parse_file(abs_fp, abs_workspace)
                    symbols = parsed["symbols"]
                    classes = parsed["classes"]
                    functions = parsed["functions"]
                    imports = parsed["imports"]
                    ast_trees[rel_fp] = parsed["raw_ast"]

                    # Complexity metrics
                    complexity = self.complexity_analyzer.calculate_complexity(rel_fp, source_content)
                except Exception:
                    # Gracefully skip parsing errors
                    continue

                # Save on cache provider
                self.cache.set(
                    rel_fp,
                    {
                        "mtime": mtime,
                        "size": size,
                        "hash": content_hash,
                        "symbols": [s.model_dump() for s in symbols],
                        "classes": [c.model_dump() for c in classes],
                        "functions": [f.model_dump() for f in functions],
                        "imports": [i.model_dump() for i in imports],
                        "complexity": complexity.model_dump(),
                    },
                )

            # Store aggregates
            for sym in symbols:
                all_symbols[sym.fully_qualified_name] = sym
            all_classes.extend(classes)
            all_functions.extend(functions)
            file_imports[rel_fp] = imports
            complexity_reports[rel_fp] = complexity

        # 4. Resolve cross-references using ReferenceFinder
        self.ref_finder.resolve_references(ast_trees, all_symbols)

        # 5. Populate In-Memory Symbol Index
        self.indexer.clear()
        for fqn, sym in all_symbols.items():
            self.indexer.index_symbols(sym.file_path, [sym])

        # 6. Build dependency graphs
        dep_graph = self.dep_analyzer.analyze_dependencies(abs_workspace, file_imports)

        # 7. Build call graph
        call_graph = build_call_graph(ast_trees, list(all_symbols.values()))

        # 8. Find duplicated code blocks
        duplicates = self.dup_detector.find_duplicates(ast_trees)

        # 9. Dead code analyzer
        dead_code = self.dead_analyzer.find_dead_code(
            python_files, all_symbols, file_imports, call_graph
        )

        # Save Cache file
        self.cache.save()

        # Compute global summary metrics
        total_loc = sum(report.total_loc for report in complexity_reports.values())
        total_complexity = sum(report.cyclomatic_complexity for report in complexity_reports.values())
        total_methods = sum(len(c.methods) for c in all_classes)

        summary = RepositoryIntelligenceSummary(
            total_classes=len(all_classes),
            total_functions=len(all_functions),
            total_methods=total_methods,
            total_variables=len([s for s in all_symbols.values() if s.symbol_type == "variable"]),
            total_loc=total_loc,
            total_complexity=total_complexity,
        )

        duration = time.perf_counter() - start_time

        meta = AnalysisMetadata(
            scan_time=duration,
            analyzed_files=len(python_files),
            python_version="Python 3.14",
            cache_used=cache_used,
        )

        return IntelligenceReport(
            summary=summary,
            symbols=all_symbols,
            classes=all_classes,
            functions=all_functions,
            dependency_graph=dep_graph,
            call_graph=call_graph,
            complexity_reports=complexity_reports,
            duplicates=duplicates,
            dead_code=dead_code,
            metadata=meta,
        )
