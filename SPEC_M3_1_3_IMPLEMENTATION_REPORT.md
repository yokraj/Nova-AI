# SPEC M3.1.3 - Code Intelligence Engine Implementation Report

## Architecture & SOLID Compliance

The **Code Intelligence Engine** implements Python AST scanning, symbol lookup indexes, call graphs, import graphs, cyclomatic and cognitive complexity metrics, code duplications, and dead code analyzers. It is organized into single-responsibility modules:

1.  **Single Responsibility Principle (SRP)**:
    *   `ast_parser.py`: Solely handles syntax tree walking and node feature extraction.
    *   `symbol_index.py`: Solely registers symbols and manages lookup tables.
    *   `dependency_graph.py`: Coordinates imports mapping.
    *   `complexity.py`: Computes cyclomatic and cognitive complexity scores.
    *   `duplicate_detector.py`: Matches AST subtrees to flag duplicate structures.
    *   `dead_code.py`: Performs unused checks on imports, variables, and scopes.
2.  **Open-Closed Principle (OCP)**:
    *   Interfaces like `ASTParser` and `SemanticSearcher` are defined in `interfaces.py`. New language parsers (e.g. JavaScript, Go) can be registered without modifying the `CodeIntelligenceAnalyzer` client code.
3.  **Liskov Substitution Principle (LSP)**:
    *   `PythonASTParser` implements `ASTParser`. Different language parsing subclasses can be substituted transparently.
4.  **Interface Segregation Principle (ISP)**:
    *   Distinct interfaces are maintained (`ASTParser`, `SymbolIndexer`, `ComplexityAnalyzer`) rather than introducing a monolithic code analysis interface.
5.  **Dependency Inversion Principle (DIP)**:
    *   `CodeIntelligenceAnalyzer` depends on interfaces (`ASTParser`, `CacheProvider`, `SemanticSearcher`) to enable loose coupling.

---

## DDD Boundaries

*   **Bounded Context**: The code intelligence domain is modeled as a core sub-domain of the Software Engineering Bounded Context.
*   **Aggregate Root**: `IntelligenceReport` is the aggregate root encompassing call graphs, dependencies, complexities, dead code declarations, and symbol indexes.
*   **Value Objects**: `Symbol`, `ImportInfo`, `ComplexityReport`, and `ASTNodeInfo` represent immutable snapshot attributes of parsed syntax.

---

## AST Design & Multi-Language Extensibility

*   **Python AST Visitor**: Extends `ast.NodeVisitor` to collect classes, async/sync methods, parameters, and variable assignments, tracking exact line and column numbers.
*   **Multi-Language Extensibility**: The `ASTParser` interface exposes `parse_file(file_path, root_path) -> Dict[str, Any]` which returns standard keys (`symbols`, `classes`, `functions`, `imports`, `methods`). Any third-party parser (e.g. Tree-sitter or language-specific compiler CLI output) can be wrapped inside an `ASTParser` subclass for other languages.

---

## Dependency & Call Graph Architecture

*   **Dependency Graph**: Utilizes `ImportResolver` to map absolute and relative imports to actual file paths inside the workspace. Uses a Depth-First Search (DFS) cycle-detection algorithm to locate circular import chains (e.g., `A -> B -> A`).
*   **Call Graph**: Traverses AST nodes, extracting target names and attributes from `ast.Call` nodes. These call targets are resolved against the symbol index to map caller fully qualified names to callee fully qualified names. It identifies direct recursion if a caller maps to its own name.

---

## Caching Strategy & Performance Considerations

*   **Incremental Cache**: Stores modification times (`mtime`), file sizes, and content SHA256 hashes inside `.nova/intelligence_cache.json`.
*   **AST Cache Hits**: If a file is unmodified, its parsed symbol list, class metadata, function metadata, and complexity metrics are loaded directly from the JSON cache, skipping file loading and syntax parsing.
*   **Lazy Loading**: The orchestrator scans the filesystem to check hashes first, loading files and parsing AST trees only on cache misses, keeping memory utilization minimal for large repositories.

---

## Integration Details

*   **Exposed Property**: Exposes `self.code_intelligence` on the `SoftwareEngineerAgent`.
*   **Dependency Injection**: The engine can be injected or consumed by code review and debugging pipelines, allowing agents to query symbols or call graphs semantically.
